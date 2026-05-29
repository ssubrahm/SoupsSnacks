"""Conversational context and follow-up resolution (ChatGPT-style multi-turn)."""

from __future__ import annotations

from typing import Any

from .followup import (
    FollowupResult,
    build_top_customers_intent_from_followup,
    classify_top_customers_followup,
    extract_tie_count_from_message,
    infer_query_params_from_assistant_message,
    is_customer_conversation_context,
    is_tie_clarification_message,
)
from .followup_llm import resolve_followup_with_llm


CUSTOMER_PENDING_INTENTS = frozenset({'show_top_customers', 'refine_top_customers'})


def build_customer_refinement_context(
    params: dict[str, Any],
    customer_count: int,
    assistant_message: str = '',
) -> dict[str, Any] | None:
    """Persist context so natural follow-ups can refine a customer list."""
    if customer_count <= 1:
        return None
    qp = {
        'months': params.get('months', 6),
        'start_date': params.get('start_date'),
        'end_date': params.get('end_date'),
        'sort_by': params.get('sort_by', 'profit'),
        'top_tier_only': params.get('top_tier_only', False),
        'singular_customer_query': False,
        'include_orders': params.get('include_orders', True),
    }
    return {
        'pending_intent': 'refine_top_customers',
        'query_params': qp,
        'result_count': customer_count,
        'clarification_question': assistant_message,
        'topic': 'top_customers',
    }


def build_tie_clarification_context(
    query_params: dict[str, Any],
    tie_count: int,
    assistant_message: str,
) -> dict[str, Any]:
    return {
        'pending_intent': 'show_top_customers',
        'query_params': query_params,
        'tie_count': tie_count,
        'clarification_question': assistant_message,
        'topic': 'top_customers',
    }


def pending_context_from_history(
    history: list[dict[str, str]] | None,
) -> dict[str, Any] | None:
    if not history:
        return None
    for entry in reversed(history):
        if entry.get('role') == 'assistant' and entry.get('pending_context'):
            return entry['pending_context']
    return None


def _resolve_with_rules(message: str, context: dict[str, Any]) -> FollowupResult:
    tie_count = context.get('tie_count') or context.get('result_count')
    return classify_top_customers_followup(message, tie_count)


def _is_likely_new_query(message: str) -> bool:
    """Detect when the user is starting a new topic, not refining the current one."""
    lower = message.strip().lower()
    new_topic_signals = [
        'unpaid',
        'outstanding',
        'order',
        'orders',
        'product',
        'menu',
        'catalog',
        'pickle',
        'what do we sell',
        'help',
        'what can you',
    ]
    if any(signal in lower for signal in new_topic_signals):
        return True
    if len(lower.split()) > 12:
        return True
    return False


def _looks_like_short_followup(message: str) -> bool:
    lower = message.strip().lower()
    if len(lower.split()) <= 8:
        return True
    hints = (
        'show', 'only', 'just', 'all', 'first', 'top', 'yes', 'no',
        'one', 'them', 'everyone', 'please', 'now',
    )
    return any(h in lower for h in hints)


def resolve_customer_followup_intent(
    message: str,
    context: dict[str, Any],
    history: list[dict[str, str]] | None = None,
    *,
    use_llm: bool = True,
) -> dict[str, Any] | None:
    """
    Resolve a customer ranking follow-up using rules, then optional LLM.
    Returns a top_customers/help intent dict, or None if not applicable.
    """
    if not is_customer_conversation_context(context):
        return None

    if _is_likely_new_query(message):
        return None

    qp = dict(context.get('query_params') or {})
    followup = _resolve_with_rules(message, context)

    if followup.action == 'unknown' and use_llm:
        llm_result = resolve_followup_with_llm(message, context, history)
        if llm_result:
            followup = llm_result

    intent = build_top_customers_intent_from_followup(followup, qp)
    if intent:
        return intent

    if followup.action == 'unknown' and _looks_like_short_followup(message):
        return _contextual_unknown_response(context)

    return None


def _contextual_unknown_response(context: dict[str, Any]) -> dict[str, Any]:
    """Helpful reply when we have context but cannot parse the follow-up."""
    count = context.get('tie_count') or context.get('result_count') or 'all'
    return {
        'intent': 'help',
        'confidence': 0.9,
        'params': {},
        'reply': (
            f"I have **{count} customers** in context. You can say things like "
            f"**\"show all {count}\"**, **\"only 6\"**, **\"first 3\"**, or **\"just one\"** — "
            "whatever feels natural."
        ),
    }


def resolve_followup_from_history(
    message: str,
    history: list[dict[str, str]] | None,
    *,
    use_llm: bool = True,
) -> dict[str, Any] | None:
    """Recover follow-up intent from chat history when session context was lost."""
    if not history:
        return None

    pending = pending_context_from_history(history)
    if pending and is_customer_conversation_context(pending):
        intent = resolve_customer_followup_intent(
            message, pending, history, use_llm=use_llm
        )
        if intent:
            return intent

    last_assistant = None
    for entry in reversed(history):
        if entry.get('role') == 'assistant':
            last_assistant = entry.get('content', '')
            break

    if not last_assistant or not is_tie_clarification_message(last_assistant):
        return None

    tie_count = extract_tie_count_from_message(last_assistant)
    qp = infer_query_params_from_assistant_message(last_assistant)
    context = build_tie_clarification_context(qp, tie_count or 0, last_assistant)
    return resolve_customer_followup_intent(message, context, history, use_llm=use_llm)


def resolve_clarification_reply(
    message: str,
    clarification_context: dict[str, Any],
    history: list[dict[str, str]] | None = None,
    *,
    use_llm: bool = True,
) -> dict[str, Any] | None:
    """Turn a clarification reply into a structured intent."""
    pending = clarification_context.get('pending_intent')
    text = message.strip()

    if pending == 'product_choice':
        return {
            'intent': 'list_orders',
            'confidence': 0.9,
            'params': {
                'product_search': text,
                'product_units': [],
            },
            'reply': None,
        }

    if is_customer_conversation_context(clarification_context):
        return resolve_customer_followup_intent(
            text, clarification_context, history, use_llm=use_llm
        )

    return None


def has_active_conversation_context(
    clarification_context: dict[str, Any] | None,
    history: list[dict[str, str]] | None,
) -> bool:
    if clarification_context and is_customer_conversation_context(clarification_context):
        return True
    pending = pending_context_from_history(history)
    return bool(pending and is_customer_conversation_context(pending))
