"""LLM fallback for ambiguous conversational follow-ups."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

from .followup import FollowupResult


FOLLOWUP_ACTIONS = ('show_all', 'show_one', 'show_limit', 'decline', 'new_query')


def resolve_followup_with_llm(
    message: str,
    context: dict[str, Any],
    history: list[dict[str, str]] | None = None,
) -> FollowupResult | None:
    """
    Use LLM to interpret a follow-up when rule matching fails.
    Returns None if LLM unavailable or user is starting a new topic.
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None

    model = getattr(settings, 'OPENAI_MODEL', None) or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    base_url = getattr(settings, 'OPENAI_BASE_URL', None) or os.getenv(
        'OPENAI_BASE_URL', 'https://api.openai.com/v1'
    )

    pending = context.get('pending_intent', '')
    tie_count = context.get('tie_count') or context.get('result_count')
    query_params = context.get('query_params') or {}
    last_question = context.get('clarification_question', '')

    system = f"""You resolve short follow-up messages in a SoupsSnacks business analytics chat.

The assistant previously asked about customer rankings or showed a customer list.
Context:
- pending_intent: {pending}
- tied_or_shown_count: {tie_count}
- query_params: {json.dumps(query_params)}
- last_assistant_message: {last_question[:500] if last_question else '(see history)'}

Classify the user's follow-up into ONE action:
- show_all: user wants the complete tied list (e.g. "yes", "all of them", "show everyone", "all 12", "12 now" when 12 are tied)
- show_one: user wants exactly one customer (e.g. "just one", "first one", "pick one")
- show_limit: user wants a specific count less than the total (e.g. "only 6", "first 6", "top 3", "just show 5", bare "6")
- decline: user declines (e.g. "no", "never mind", "skip")
- new_query: user is asking something unrelated — do NOT guess

For show_limit, set "limit" to the integer count (1-50).
Respond with JSON only: {{"action": "...", "limit": null or int, "confidence": 0.0-1.0}}
"""

    messages = [{'role': 'system', 'content': system}]
    for h in (history or [])[-8:]:
        messages.append({'role': h['role'], 'content': h.get('content', '')})
    messages.append({'role': 'user', 'content': message})

    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.0,
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode('utf-8'))
        parsed = json.loads(body['choices'][0]['message']['content'])
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        KeyError,
        json.JSONDecodeError,
        TimeoutError,
        OSError,
    ):
        return None

    action = parsed.get('action', 'new_query')
    confidence = float(parsed.get('confidence') or 0)
    if action not in FOLLOWUP_ACTIONS or action == 'new_query' or confidence < 0.5:
        return None

    limit = parsed.get('limit')
    if action == 'show_limit':
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return None
        if not 1 <= limit <= 50:
            return None

    return FollowupResult(action=action, limit=limit if action == 'show_limit' else None)
