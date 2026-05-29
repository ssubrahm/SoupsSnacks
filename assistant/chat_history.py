"""Persist and restore Ask chat sessions in the database."""

from __future__ import annotations

from typing import Any

from .models import ChatMessage, ChatSession


def get_or_create_active_session(user, session_id: int | None = None) -> ChatSession:
    if session_id:
        session = ChatSession.objects.filter(id=session_id, user=user).first()
        if session:
            return session

    active = ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at').first()
    if active:
        return active

    return ChatSession.objects.create(user=user, title='New chat')


def start_new_session(user) -> ChatSession:
    ChatSession.objects.filter(user=user, is_active=True).update(is_active=False)
    return ChatSession.objects.create(user=user, title='New chat', is_active=True)


def deactivate_session(user, session_id: int | None = None) -> None:
    qs = ChatSession.objects.filter(user=user, is_active=True)
    if session_id:
        qs = qs.filter(id=session_id)
    qs.update(is_active=False)


def _maybe_set_title(session: ChatSession, user_message: str) -> None:
    if session.title and session.title != 'New chat':
        return
    title = user_message.strip().replace('\n', ' ')
    if len(title) > 80:
        title = title[:77] + '...'
    session.title = title or 'New chat'
    session.save(update_fields=['title', 'updated_at'])


def save_turn(
    session: ChatSession,
    user_message: str,
    assistant_message: str,
    *,
    response_type: str = 'text',
    response_data: dict | None = None,
    intent: str | None = None,
    pending_context: dict | None = None,
) -> None:
    _maybe_set_title(session, user_message)
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message,
    )
    ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=assistant_message,
        response_type=response_type or 'text',
        response_data=response_data,
        intent=intent or '',
        pending_context=pending_context,
    )
    session.save(update_fields=['updated_at'])


def session_to_messages(session: ChatSession) -> list[dict[str, Any]]:
    """Convert DB messages to frontend message shape."""
    rows = session.messages.order_by('created_at')
    result = []
    for row in rows:
        msg: dict[str, Any] = {
            'id': f'db-{row.id}',
            'role': row.role,
            'content': row.content,
        }
        if row.role == 'assistant':
            msg['type'] = row.response_type or 'text'
            msg['data'] = row.response_data
            if row.pending_context:
                msg['pendingContext'] = row.pending_context
        result.append(msg)
    return result


def list_sessions(user, limit: int = 20) -> list[dict[str, Any]]:
    sessions = ChatSession.objects.filter(user=user).order_by('-updated_at')[:limit]
    return [
        {
            'id': s.id,
            'title': s.title or 'New chat',
            'is_active': s.is_active,
            'updated_at': s.updated_at.isoformat(),
            'message_count': s.messages.count(),
        }
        for s in sessions
    ]


def load_session(user, session_id: int) -> dict[str, Any] | None:
    session = ChatSession.objects.filter(id=session_id, user=user).first()
    if not session:
        return None
    ChatSession.objects.filter(user=user, is_active=True).exclude(id=session.id).update(
        is_active=False
    )
    if not session.is_active:
        session.is_active = True
        session.save(update_fields=['is_active', 'updated_at'])
    return {
        'session_id': session.id,
        'title': session.title,
        'messages': session_to_messages(session),
    }
