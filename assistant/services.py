"""Orchestrate assistant chat turns."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from . import query_engine
from .conversation import (
    build_customer_refinement_context,
    pending_context_from_history,
    resolve_clarification_reply,
    resolve_followup_from_history,
)
from .intent_parser import parse_intent


HELP_TEXT = """I can help you explore your SoupsSnacks business data. Try asking:

• **Orders** — "Show all orders for Tender Mango Pickle 500g and 1Kg"
• **Customers** — "Who is my most profitable customer in the last 6 months?"
• **Payments** — "Show unpaid orders"
• **Menu** — "What pickle products do we sell?"
• **Daily offerings** — "What's on today's menu?"
• **Payments** — "Show payment trends for the last 3 months"

Ask in plain English — I'll clarify if something is ambiguous."""


def _date_range_from_params(params: dict[str, Any]) -> tuple[date | None, date | None]:
    start = params.get('start_date')
    end = params.get('end_date')
    months = params.get('months')

    end_date = date.fromisoformat(end) if end else None
    start_date = date.fromisoformat(start) if start else None

    if months and not start_date:
        end_date = end_date or date.today()
        start_date = end_date - timedelta(days=int(months) * 30)

    return start_date, end_date


def _resolve_product_ids(params: dict[str, Any]) -> tuple[list[int], str | None, dict | None]:
    """
    Returns (product_ids, product_search, clarification_payload).
    clarification_payload set if user must pick among options.
    """
    products, _ = query_engine.resolve_products(
        product_names=params.get('product_names'),
        product_units=params.get('product_units'),
        product_search=params.get('product_search'),
    )

    if not products:
        search = params.get('product_search') or (
            ' '.join(params.get('product_names') or [])
        )
        if search:
            return [], search, None
        return [], None, None

    if len(products) > 8 and not params.get('product_units'):
        options = [f"{p.name} {p.unit}".strip() for p in products[:12]]
        return [], None, {
            'pending_intent': 'product_choice',
            'clarification_question': 'Several products match. Which one(s) did you mean?',
            'clarification_options': options,
        }

    return [p.id for p in products], None, None


def execute_intent(intent: dict[str, Any], user_role: str) -> dict[str, Any]:
    """Run parsed intent and return response payload for the frontend."""
    name = intent.get('intent', 'unknown')
    params = intent.get('params') or {}
    preview = intent.get('reply')

    is_operator = user_role in ('admin', 'operator')

    if name == 'help':
        return {
            'type': 'text',
            'message': preview or HELP_TEXT,
            'data': None,
        }

    if name == 'clarify':
        return {
            'type': 'clarification',
            'message': params.get('clarification_question') or 'Could you tell me a bit more?',
            'data': {
                'options': params.get('clarification_options') or [],
            },
        }

    if name in ('list_orders', 'top_customers', 'unpaid_orders', 'daily_offerings', 'payment_trends') and not is_operator:
        return {
            'type': 'text',
            'message': 'Order and customer analytics are available to operators and admins. '
            'You can ask about the product menu instead.',
            'data': None,
        }

    if name == 'list_orders':
        product_ids, product_search, clarification = _resolve_product_ids(params)
        if clarification:
            return {
                'type': 'clarification',
                'message': clarification['clarification_question'],
                'data': {
                    'options': clarification['clarification_options'],
                    'pending_intent': clarification['pending_intent'],
                },
            }

        start_date, end_date = _date_range_from_params(params)
        data = query_engine.list_orders(
            product_ids=product_ids or None,
            product_search=product_search,
            start_date=start_date,
            end_date=end_date,
            date_field=params.get('date_field', 'order_date'),
            status=params.get('status'),
            payment_status=params.get('payment_status'),
            limit=int(params.get('limit', 100)),
        )

        if data['count'] == 0:
            return {
                'type': 'text',
                'message': preview or 'No orders matched your question. Try widening the date range or product name.',
                'data': data,
            }

        product_label = params.get('product_search') or ', '.join(params.get('product_names') or ['selected products'])
        msg = preview or f"Found **{data['count']}** order(s) for {product_label}."
        if start_date or end_date:
            msg += f" ({start_date or '…'} to {end_date or '…'})"

        return {'type': 'orders', 'message': msg, 'data': data}

    if name == 'top_customers':
        start_date, end_date = _date_range_from_params(params)
        months = int(params.get('months') or 6)
        sort_by = params.get('sort_by', 'profit')
        data = query_engine.top_customers(
            months=months,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            limit=int(params.get('limit', 5)),
            top_tier_only=bool(params.get('top_tier_only', False)),
            include_orders=params.get('include_orders', True),
        )

        if not data['customers']:
            return {
                'type': 'text',
                'message': 'No customer activity found for that period.',
                'data': data,
            }

        top = data['customers'][0]
        sort_label = 'profit' if sort_by == 'profit' else 'revenue'
        count = len(data['customers'])
        peak = data.get('peak_value', 0)
        top_tier = data.get('top_tier_only', False)
        singular = bool(params.get('singular_customer_query'))
        force_show_all = bool(params.get('force_show_all'))
        force_show_one = bool(params.get('force_show_one'))
        force_limit = params.get('force_limit')

        query_params = {
            'months': months,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'sort_by': sort_by,
            'top_tier_only': top_tier,
            'singular_customer_query': singular,
            'include_orders': True,
        }

        # Singular "who is my best customer" with a tie → ask before listing everyone
        if singular and count > 1 and not force_show_all and not force_show_one and not force_limit:
            sample_names = [c['customer_name'] for c in data['customers'][:3]]
            sample_text = ', '.join(sample_names)
            if count > 3:
                sample_text += f', and {count - 3} more'

            tie_msg = (
                f"There isn't just one — **{count} customers** are tied for the highest "
                f"**{sort_label}** at **₹{peak:,.2f}** ({data['start_date']} to {data['end_date']}). "
                f"Examples include **{sample_text}**. "
                f"Would you like me to show all {count}, or just some of them?"
            )

            return {
                'type': 'clarification',
                'message': tie_msg,
                'data': {
                    'pending_intent': 'show_top_customers',
                    'options': [
                        f'Show all {count} tied customers',
                        'Show only the first one',
                        'Show first 6',
                    ],
                    'query_params': query_params,
                    'tie_count': count,
                },
            }

        if force_show_one and count >= 1:
            data = {**data, 'customers': [data['customers'][0]]}
            top = data['customers'][0]
            count = 1
        elif force_limit and count >= 1:
            limit_n = int(force_limit)
            data = {**data, 'customers': data['customers'][:limit_n]}
            top = data['customers'][0]
            count = len(data['customers'])

        if preview:
            msg = preview
        elif count == 1:
            msg = (
                f"Top customer by **{sort_label}** ({data['start_date']} to {data['end_date']}): "
                f"**{top['customer_name']}** — ₹{top['total_profit']:,.2f} profit, "
                f"₹{top['total_spent']:,.2f} revenue across {top['order_count']} order(s)."
            )
        elif force_limit and count >= 1:
            msg = (
                f"Showing **{count}** customer{'s' if count != 1 else ''} "
                f"by **{sort_label}** ({data['start_date']} to {data['end_date']}). "
                f"Highest: **{top['customer_name']}** at ₹{peak:,.2f}."
            )
        elif top_tier or force_show_all:
            msg = (
                f"**{count} customer{'s' if count != 1 else ''}** tied for highest **{sort_label}** "
                f"at **₹{peak:,.2f}** ({data['start_date']} to {data['end_date']})."
            )
        else:
            msg = (
                f"**Top {count} customers** by **{sort_label}** "
                f"({data['start_date']} to {data['end_date']}). "
                f"Highest: **{top['customer_name']}** at ₹{peak:,.2f}."
            )

        return {'type': 'customers', 'message': msg, 'data': data}

    if name == 'unpaid_orders':
        data = query_engine.unpaid_orders()
        msg = preview or f"Found **{data['count']}** unpaid or partially paid order(s)."
        return {'type': 'orders', 'message': msg, 'data': data}

    if name == 'product_catalog':
        data = query_engine.product_catalog_summary(params.get('search'))
        msg = preview or f"Showing **{data['count']}** product(s) from your menu."
        return {'type': 'products', 'message': msg, 'data': data}

    if name == 'daily_offerings':
        offering_date = params.get('offering_date')
        od = date.fromisoformat(offering_date) if offering_date else None
        days_back = int(params.get('days_back') or 7)
        start_date = date.today() - timedelta(days=days_back) if not od else None
        data = query_engine.daily_offerings(
            offering_date=od,
            start_date=start_date,
            active_only=bool(params.get('active_only', False)),
            limit=int(params.get('limit', 10)),
        )
        if not data['offerings']:
            when = offering_date or f'the last {days_back} days'
            return {
                'type': 'text',
                'message': preview or f'No daily offerings found for {when}.',
                'data': data,
            }
        if od:
            msg = preview or f"**Daily offering** for **{od.isoformat()}** — {data['count']} menu(s)."
        else:
            msg = preview or f"Showing **{data['count']}** recent daily offering(s)."
        return {'type': 'offerings', 'message': msg, 'data': data}

    if name == 'payment_trends':
        start_date, end_date = _date_range_from_params(params)
        months = int(params.get('months') or 6)
        data = query_engine.payment_trends(
            months=months,
            start_date=start_date,
            end_date=end_date,
            method=params.get('method'),
        )
        if data['total_count'] == 0:
            return {
                'type': 'text',
                'message': preview or 'No payments recorded for that period.',
                'data': data,
            }
        method_note = f" ({params['method']})" if params.get('method') else ''
        msg = preview or (
            f"**Payment trends**{method_note} ({data['start_date']} to {data['end_date']}): "
            f"**{data['total_count']}** payment(s) totalling **₹{data['total_amount']:,.2f}**."
        )
        return {'type': 'payment_trends', 'message': msg, 'data': data}

    return {
        'type': 'text',
        'message': preview
        or "I'm not sure how to answer that yet. Try asking about orders, customers, payments, or your menu.",
        'data': None,
    }


def handle_message(
    message: str,
    history: list[dict[str, str]] | None,
    clarification_context: dict | None,
    user_role: str,
) -> dict[str, Any]:
    """Full turn: parse → execute → return assistant response + updated context."""
    if not clarification_context and history:
        clarification_context = pending_context_from_history(history)

    intent = None

    if clarification_context:
        intent = resolve_clarification_reply(message, clarification_context, history)

    if not intent:
        intent = resolve_followup_from_history(message, history)

    if not intent:
        intent = parse_intent(message, history, clarification_context)

    result = execute_intent(intent, user_role)

    new_context = None
    if result['type'] == 'clarification':
        new_context = {
            'pending_intent': result['data'].get('pending_intent', 'general'),
            'clarification_question': result['message'],
            'options': result['data'].get('options', []),
            'query_params': result['data'].get('query_params'),
            'tie_count': result['data'].get('tie_count'),
            'topic': 'top_customers',
        }
    elif result['type'] == 'customers' and intent.get('intent') == 'top_customers':
        customers = (result.get('data') or {}).get('customers') or []
        new_context = build_customer_refinement_context(
            intent.get('params') or {},
            len(customers),
            result.get('message', ''),
        )

    return {
        'intent': intent.get('intent'),
        'response': result,
        'clarification_context': new_context,
    }
