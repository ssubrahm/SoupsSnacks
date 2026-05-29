"""Classify natural-language follow-ups to customer ranking queries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal


FollowupAction = Literal['show_all', 'show_one', 'show_limit', 'decline', 'unknown']


@dataclass
class FollowupResult:
    action: FollowupAction
    limit: int | None = None


# Conversational limit phrases humans use in chat
_LIMIT_PATTERNS = [
    r'\b(?:first|top)\s+(\d+)\b',
    r'\b(?:show|list|give)\s+(?:me\s+)?(?:the\s+)?(?:first|top)\s+(\d+)\b',
    r'\b(?:show|list|give)\s+(?:me\s+)?(?:only\s+)?(\d+)\b(?!\s*(?:orders?|items?))',
    r'\btop\s+(\d+)\s+customers?\b',
    # "only 6 now", "just 6", "maybe 6"
    r'\b(?:only|just|maybe|about|like|need|want|do)\s+(\d+)\b',
    r'\b(\d+)\s+(?:please|thanks|for now|of them|customers?|people|rows?)\b',
    r'\b(?:limit|cap)\s+(?:to\s+)?(?:the\s+)?(\d+)\b',
    r'\b(?:show|give|list)\s+(?:me\s+)?(\d+)\b(?!\s*(?:orders?|items?))',
]

# Bare number at start/end of short replies
_BARE_NUMBER = re.compile(
    r'^\s*(?:ok|okay|yeah|sure|then|now|actually|hmm)?\s*(\d+)\s*(?:please|thanks|now|ok|then|only)?\s*$',
    re.I,
)

_SHOW_ALL_PHRASES = (
    'all of them',
    'all of those',
    'everyone',
    'every one',
    'the full list',
    'full list',
    'complete list',
    'show them all',
    'see them all',
    'list them all',
    'give me all',
    'show everyone',
)


def extract_limit(message: str, tie_count: int | None = None) -> int | None:
    """Extract a numeric limit from conversational phrases."""
    lower = message.strip().lower()

    for pat in _LIMIT_PATTERNS:
        m = re.search(pat, lower)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 50:
                return n

    bare = _BARE_NUMBER.match(lower)
    if bare:
        n = int(bare.group(1))
        # "12" when 12 are tied → show all, not limit (handled by caller)
        if tie_count and n == tie_count:
            return None
        if 1 <= n <= 50:
            return n

    return None


def is_show_all(message: str, tie_count: int | None = None) -> bool:
    lower = message.strip().lower()

    # Limit phrases take precedence over show-all heuristics
    if extract_limit(message, tie_count) is not None and not re.search(r'\ball\b', lower):
        return False

    if any(phrase in lower for phrase in _SHOW_ALL_PHRASES):
        return True

    if re.search(r'\b(?:show|see|list|display|give)\s+(?:me\s+)?(?:the\s+)?all\b', lower):
        return True
    if re.search(r'\ball\s+\d+\b', lower):
        return True
    if tie_count and str(tie_count) in lower and 'all' in lower:
        return True
    # "12 now" when 12 tied — number alone means show all
    if tie_count:
        bare = _BARE_NUMBER.match(lower)
        if bare and int(bare.group(1)) == tie_count:
            return True
        if re.fullmatch(rf'\s*{tie_count}\s*(?:now|please|ok|thanks)?\s*', lower):
            return True
    if re.search(r'\b(yes|yeah|yep|yup|sure|ok|okay|please|go ahead|do it|show them|absolutely|definitely)\b', lower):
        return True
    if 'show me all' in lower or lower.startswith('now show all'):
        return True
    if re.search(r'\bshow\s+all\b', lower):
        return True
    return False


def is_show_one(message: str) -> bool:
    lower = message.strip().lower()
    # "only 6" is a limit, not "only one"
    if re.search(r'\b(?:only|just)\s+\d+\b', lower):
        n_match = re.search(r'\b(?:only|just)\s+(\d+)\b', lower)
        if n_match and int(n_match.group(1)) != 1:
            return False
    if extract_limit(message) is not None:
        return False
    return any(
        phrase in lower
        for phrase in [
            'first one',
            'only one',
            'just one',
            'just the first',
            'single customer',
            'one only',
            'top one',
            'show only the first one',
            'pick one',
            'any one',
            'whichever one',
        ]
    )


def is_decline(message: str) -> bool:
    lower = message.strip().lower().strip('.!')
    if lower in ('no', 'nope', 'nah'):
        return True
    return any(
        phrase in lower
        for phrase in [
            'no thanks',
            'no thank you',
            'never mind',
            'nevermind',
            'skip',
            'cancel',
            'not now',
            'leave it',
            'forget it',
        ]
    )


def classify_top_customers_followup(
    message: str, tie_count: int | None = None
) -> FollowupResult:
    """
    Classify a follow-up to a customer ranking / tie clarification.

    Priority: decline → show_one → show_limit → show_all → unknown
    """
    lower = message.strip().lower()

    if is_decline(message):
        return FollowupResult(action='decline')

    if is_show_one(message):
        return FollowupResult(action='show_one')

    limit = extract_limit(message, tie_count)
    if limit is not None and not re.search(r'\ball\b', lower):
        if tie_count and limit == tie_count:
            return FollowupResult(action='show_all')
        return FollowupResult(action='show_limit', limit=limit)

    if is_show_all(message, tie_count):
        return FollowupResult(action='show_all')

    if 'tied customer' in lower and 'all' in lower:
        return FollowupResult(action='show_all')

    return FollowupResult(action='unknown')


def is_customer_conversation_context(context: dict[str, Any] | None) -> bool:
    if not context:
        return False
    return context.get('pending_intent') in (
        'show_top_customers',
        'refine_top_customers',
    )


def build_top_customers_intent_from_followup(
    followup: FollowupResult,
    query_params: dict[str, Any],
) -> dict[str, Any] | None:
    """Build a top_customers intent dict from classified follow-up."""
    qp = dict(query_params or {})

    if followup.action == 'decline':
        return {
            'intent': 'help',
            'confidence': 1.0,
            'params': {},
            'reply': 'No problem. Ask again anytime if you want the full list.',
        }

    if followup.action == 'show_one':
        qp['force_show_one'] = True
        qp['singular_customer_query'] = False
        return {'intent': 'top_customers', 'confidence': 1.0, 'params': qp, 'reply': None}

    if followup.action == 'show_limit' and followup.limit:
        qp['force_show_all'] = False
        qp['force_limit'] = followup.limit
        qp['top_tier_only'] = qp.get('top_tier_only', True)
        qp['singular_customer_query'] = False
        return {'intent': 'top_customers', 'confidence': 1.0, 'params': qp, 'reply': None}

    if followup.action == 'show_all':
        qp['force_show_all'] = True
        qp['singular_customer_query'] = False
        return {'intent': 'top_customers', 'confidence': 1.0, 'params': qp, 'reply': None}

    return None


def is_tie_clarification_message(content: str) -> bool:
    lower = content.lower().replace('\u2019', "'").replace('\u2018', "'")
    is_tie = (
        "isn't just one" in lower
        or 'isnt just one' in lower
        or 'tied for' in lower
        or 'tied at' in lower
    )
    asks = (
        'would you like' in lower
        or 'show all' in lower
        or 'see all' in lower
    )
    return is_tie and asks


def infer_query_params_from_assistant_message(content: str) -> dict[str, Any]:
    """Best-effort rebuild query params from assistant tie message."""
    lower = content.lower()
    sort_by = 'profit' if 'profit' in lower else 'revenue'
    return {
        'months': 6,
        'sort_by': sort_by,
        'top_tier_only': True,
        'singular_customer_query': True,
        'include_orders': True,
    }


def extract_tie_count_from_message(content: str) -> int | None:
    m = re.search(r'(\d+)\s+customers', content.lower())
    return int(m.group(1)) if m else None
