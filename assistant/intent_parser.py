"""Parse natural language into structured assistant intents."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, timedelta
from typing import Any

from django.conf import settings

from .query_engine import get_catalog_context


INTENTS = (
    'list_orders',
    'top_customers',
    'unpaid_orders',
    'product_catalog',
    'daily_offerings',
    'payment_trends',
    'help',
    'clarify',
    'unknown',
)


def _months_from_text(text: str) -> int | None:
    lower = text.lower()
    patterns = [
        (r'last\s+(\d+)\s+months?', 1),
        (r'past\s+(\d+)\s+months?', 1),
        (r'(\d+)\s+months?', 1),
        (r'last\s+month', None),
        (r'last\s+week', None),
        (r'last\s+(\d+)\s+days?', 1),
    ]
    for pat, group in patterns:
        m = re.search(pat, lower)
        if m:
            if group is None:
                if 'month' in pat:
                    return 1
                if 'week' in pat:
                    return 0  # handled as days below
            else:
                return int(m.group(group))
    if 'six months' in lower or '6 months' in lower:
        return 6
    if 'three months' in lower or '3 months' in lower:
        return 3
    if 'year' in lower or '12 months' in lower:
        return 12
    return None


def _offering_date_from_text(text: str) -> date | None:
    lower = text.lower()
    today = date.today()
    if 'today' in lower or "today's" in lower:
        return today
    if 'tomorrow' in lower:
        return today + timedelta(days=1)
    if 'yesterday' in lower:
        return today - timedelta(days=1)
    m = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    m = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        try:
            return date(y, mo, d)
        except ValueError:
            pass
    return None


def _payment_method_from_text(text: str) -> str | None:
    lower = text.lower()
    mapping = {
        'upi': 'upi',
        'cash': 'cash',
        'bank': 'bank_transfer',
        'transfer': 'bank_transfer',
        'card': 'card',
    }
    for key, value in mapping.items():
        if key in lower:
            return value
    return None


def _extract_product_units(text: str) -> list[str]:
    units = []
    for pat in [r'\b500g\b', r'\b1\s*kg\b', r'\b1kg\b', r'\b250g\b', r'\b250\s*ml\b', r'\b500\s*ml\b']:
        if re.search(pat, text, re.I):
            u = re.search(pat, text, re.I).group(0)
            units.append(u.replace(' ', ''))
    # normalize
    normalized = []
    for u in units:
        if u.lower() in ('1kg', '1kg'):
            normalized.append('1Kg')
        elif u.lower() == '500g':
            normalized.append('500g')
        else:
            normalized.append(u)
    return list(dict.fromkeys(normalized))


def _extract_product_name(text: str) -> str | None:
    lower = text.lower()
    # "orders of X" / "orders for X"
    for pat in [
        r'orders?\s+(?:of|for|with|containing)\s+(.+?)(?:\s+in\s+|\s+from\s+|\s+both\s+|\?|$)',
        r'show\s+(?:me\s+)?(?:all\s+)?orders?\s+(?:of|for|with)\s+(.+?)(?:\s+both|\?|$)',
        r'(?:sales|orders)\s+for\s+(.+?)(?:\?|$)',
    ]:
        m = re.search(pat, lower, re.I)
        if m:
            raw = m.group(1)
            raw = re.sub(r'\bboth\b.*', '', raw, flags=re.I)
            raw = re.sub(r'\b(500g|1\s*kg|1kg|250g)\b.*', '', raw, flags=re.I)
            return raw.strip(' .,')
    if 'tender mango pickle' in lower:
        return 'Tender Mango Pickle'
    if 'mango pickle' in lower:
        return 'Tender Mango Pickle'
    return None


def _is_singular_customer_query(text: str) -> bool:
    """True for 'who is my best customer' (not 'customers')."""
    lower = text.lower()
    if re.search(r'\bcustomers\b', lower):
        return False
    if re.search(r'\bcustomer\b', lower):
        return True
    if 'who is' in lower and any(w in lower for w in ['most', 'best', 'highest', 'valuable', 'top']):
        return True
    return False


def _extract_customer_query_mode(text: str) -> dict[str, Any]:
    """
    Decide whether to return top-N ranked customers or only the peak tier (ties at max).
    "Most valuable customers" → peak tier only, not everyone in the database.
    """
    lower = text.lower()

    m = re.search(r'\btop\s+(\d+)\b', lower)
    if m:
        return {'limit': min(int(m.group(1)), 50), 'top_tier_only': False}

    if any(w in lower for w in ['all customers', 'list all customers', 'every customer', 'rank all']):
        return {'limit': 50, 'top_tier_only': False}

    # Superlatives → only customers at the highest revenue/profit (include ties)
    if any(w in lower for w in ['most', 'best', 'highest', 'valuable', 'top customer']):
        return {'limit': 50, 'top_tier_only': True}

    return {'limit': 10, 'top_tier_only': False}


def _extract_sort_by(text: str) -> str:
    """Prefer explicit metric; revenue vs profit."""
    lower = text.lower()
    if any(w in lower for w in ['revenue', 'spent', 'spending', 'sales', 'purchase amount']):
        return 'revenue'
    if any(w in lower for w in ['profit', 'profitability', 'profitable', 'margin']):
        return 'profit'
    # "valuable" without qualifier defaults to revenue (spend-based value)
    return 'revenue'


def parse_with_rules(message: str, clarification_context: dict | None = None) -> dict[str, Any]:
    """Rule-based intent parser when LLM is unavailable."""
    text = message.strip()
    lower = text.lower()

    if clarification_context:
        pending = clarification_context.get('pending_intent')
        if pending == 'product_choice':
            # User picked from options — treat message as product label(s)
            return {
                'intent': 'list_orders',
                'confidence': 0.85,
                'params': {
                    'product_search': text,
                    'product_units': _extract_product_units(text),
                },
                'reply': None,
            }

    if any(w in lower for w in ['help', 'what can you', 'how do i', 'what do you']):
        return {
            'intent': 'help',
            'confidence': 0.9,
            'params': {},
            'reply': None,
        }

    if 'unpaid' in lower or 'outstanding' in lower or 'pending payment' in lower:
        return {
            'intent': 'unpaid_orders',
            'confidence': 0.85,
            'params': {},
            'reply': None,
        }

    if any(
        phrase in lower
        for phrase in [
            'payment trend',
            'payment trends',
            'payments by method',
            'payment breakdown',
            'payment summary',
            'how much upi',
            'how much cash',
            'payment methods',
            'collected by',
        ]
    ) or (
        'payment' in lower
        and any(w in lower for w in ['trend', 'breakdown', 'summary', 'method', 'collected', 'received'])
    ):
        months = _months_from_text(text) or 6
        params: dict[str, Any] = {'months': months}
        method = _payment_method_from_text(text)
        if method:
            params['method'] = method
        return {
            'intent': 'payment_trends',
            'confidence': 0.82,
            'params': params,
            'reply': None,
        }

    if any(
        phrase in lower
        for phrase in [
            'daily offering',
            'daily offerings',
            'daily menu',
            "today's menu",
            'todays menu',
            'what are we offering',
            'what is on the menu today',
            'offering today',
            'menu for today',
            'menu tomorrow',
        ]
    ) or (
        'offering' in lower and any(w in lower for w in ['today', 'tomorrow', 'menu', 'daily'])
    ):
        offering_date = _offering_date_from_text(text)
        params = {'active_only': 'active' in lower}
        if offering_date:
            params['offering_date'] = offering_date.isoformat()
        months = _months_from_text(text)
        if months and not offering_date:
            params['days_back'] = min(months * 30, 90)
        return {
            'intent': 'daily_offerings',
            'confidence': 0.82,
            'params': params,
            'reply': None,
        }

    if any(
        phrase in lower
        for phrase in [
            'most valuable customer',
            'most valuable customers',
            'valuable customer',
            'valuable customers',
            'top customer',
            'top customers',
            'best customer',
            'best customers',
            'profitability',
            'most profit',
            'highest profit',
            'customer by revenue',
            'customers by revenue',
            'customer revenue',
            'customers revenue',
        ]
    ) or (
        'customer' in lower
        and any(w in lower for w in ['revenue', 'profit', 'valuable', 'best', 'top'])
    ):
        months = _months_from_text(text) or 6
        query_mode = _extract_customer_query_mode(text)
        return {
            'intent': 'top_customers',
            'confidence': 0.8,
            'params': {
                'months': months,
                'sort_by': _extract_sort_by(text),
                'limit': query_mode['limit'],
                'top_tier_only': query_mode['top_tier_only'],
                'singular_customer_query': _is_singular_customer_query(text),
                'include_orders': True,
            },
            'reply': None,
        }

    if any(w in lower for w in ['order', 'orders', 'purchase', 'bought', 'sales of']):
        product_name = _extract_product_name(text)
        units = _extract_product_units(text)
        months = _months_from_text(text)
        params: dict[str, Any] = {
            'include_order_details': True,
        }
        if product_name:
            params['product_names'] = [product_name]
        if units:
            params['product_units'] = units
        if not product_name and not units:
            # try whole phrase after "orders"
            params['product_search'] = text
        if months:
            params['months'] = months
        return {
            'intent': 'list_orders',
            'confidence': 0.75,
            'params': params,
            'reply': None,
        }

    if any(w in lower for w in ['menu', 'catalog', 'products', 'what do we sell']):
        return {
            'intent': 'product_catalog',
            'confidence': 0.7,
            'params': {'search': text},
            'reply': None,
        }

    return {
        'intent': 'unknown',
        'confidence': 0.3,
        'params': {},
        'reply': None,
    }


def parse_with_llm(
    message: str,
    history: list[dict[str, str]] | None = None,
    clarification_context: dict | None = None,
) -> dict[str, Any] | None:
    """Call OpenAI-compatible API to parse intent. Returns None if unavailable."""
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None

    model = getattr(settings, 'OPENAI_MODEL', None) or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    base_url = getattr(settings, 'OPENAI_BASE_URL', None) or os.getenv(
        'OPENAI_BASE_URL', 'https://api.openai.com/v1'
    )

    catalog = get_catalog_context()
    system = f"""You are a query planner for SoupsSnacks, a home food order management app.
Parse the user's question into JSON only (no markdown).

Available intents:
- list_orders: find orders (params: product_names[], product_units[], product_search, months, start_date, end_date, status, payment_status)
- top_customers: rank customers (params: months, sort_by profit|revenue, limit, include_orders bool)
  Use limit=1 only for singular "who is my best customer". Use limit=25 when user says "customers" (plural) or asks for a list/ranking.
  If user says "by revenue", set sort_by=revenue. If "by profit", set sort_by=profit.
  Set top_tier_only=true when user asks for "most/best/highest/valuable" customers — return only those tied at the peak metric, not all customers.
  Set top_tier_only=false when user asks for "top 5" or "top 10" (explicit count).
- unpaid_orders: orders with pending/partial payment
- daily_offerings: daily menu offerings (params: offering_date ISO, days_back, active_only bool)
- payment_trends: payment totals by method (params: months, start_date, end_date, method upi|cash|bank_transfer|card|other)
- product_catalog: list menu products (params: search)
- help: user asks what you can do
- clarify: need user clarification (params: clarification_question, clarification_options[])

Product catalog (name and unit are separate fields):
{catalog}

Today is {date.today().isoformat()}.

If user mentions "500g and 1KG" for same product, set product_names=["Tender Mango Pickle"] and product_units=["500g","1Kg"] when appropriate.

Respond with JSON:
{{
  "intent": "...",
  "confidence": 0.0-1.0,
  "params": {{}},
  "clarification_question": null or string,
  "clarification_options": [],
  "reply": "brief friendly message preview"
}}
"""

    messages = [{'role': 'system', 'content': system}]
    for h in (history or [])[-6:]:
        messages.append({'role': h['role'], 'content': h['content']})
    if clarification_context:
        messages.append(
            {
                'role': 'system',
                'content': f'Pending clarification context: {json.dumps(clarification_context)}',
            }
        )
    messages.append({'role': 'user', 'content': message})

    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.1,
        'response_format': {'type': 'json_object'},
    }

    req = urllib.request.Request(
        f'{base_url.rstrip("/")}/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode('utf-8'))
        content = body['choices'][0]['message']['content']
        parsed = json.loads(content)
        if parsed.get('clarification_question'):
            parsed['intent'] = 'clarify'
            parsed['params'] = {
                'clarification_question': parsed['clarification_question'],
                'clarification_options': parsed.get('clarification_options') or [],
            }
        return parsed
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError):
        return None


def parse_intent(
    message: str,
    history: list[dict[str, str]] | None = None,
    clarification_context: dict | None = None,
) -> dict[str, Any]:
    """Parse user message — LLM first, rules fallback."""
    parsed = parse_with_llm(message, history, clarification_context)
    if parsed and parsed.get('intent') not in (None, 'unknown'):
        return parsed
    return parse_with_rules(message, clarification_context)
