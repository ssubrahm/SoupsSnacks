from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .chat_history import (
    get_or_create_active_session,
    list_sessions,
    load_session,
    save_turn,
    start_new_session,
)
from .export_csv import result_to_csv
from .services import HELP_TEXT, handle_message
from .transcribe import transcribe_audio


STARTER_PROMPTS = [
    'Show me all orders for Tender Mango Pickle 500g and 1Kg',
    'Who is my most profitable customer in the last 6 months?',
    'Show unpaid orders',
    "What's on today's menu?",
    'Show payment trends for the last 3 months',
]


class AssistantChatView(APIView):
    """Natural language business assistant."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Starter prompts, active session, and recent sessions."""
        session_id = request.query_params.get('session_id')
        active_session = get_or_create_active_session(request.user, session_id)
        payload = {
            'starters': STARTER_PROMPTS,
            'help': HELP_TEXT,
            'llm_enabled': bool(getattr(settings, 'OPENAI_API_KEY', '')),
            'voice_transcription_enabled': bool(getattr(settings, 'OPENAI_API_KEY', '')),
            'session_id': active_session.id,
            'sessions': list_sessions(request.user),
        }
        if session_id:
            loaded = load_session(request.user, int(session_id))
            if loaded:
                payload['session_id'] = loaded['session_id']
                payload['messages'] = loaded['messages']
                payload['title'] = loaded['title']
        elif active_session.messages.exists():
            payload['messages'] = load_session(request.user, active_session.id)['messages']
            payload['title'] = active_session.title
        return Response(payload)

    def post(self, request):
        message = (request.data.get('message') or '').strip()
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        session_id = request.data.get('session_id')
        session = get_or_create_active_session(request.user, session_id)

        history = request.data.get('history') or request.session.get('assistant_history') or []
        clarification_context = (
            request.data.get('clarification_context')
            or request.session.get('assistant_clarification')
        )

        if request.data.get('clear_context'):
            clarification_context = None
            request.session.pop('assistant_clarification', None)

        turn = handle_message(
            message=message,
            history=history,
            clarification_context=clarification_context,
            user_role=request.user.role,
        )

        history = (history + [
            {'role': 'user', 'content': message},
            {'role': 'assistant', 'content': turn['response']['message']},
        ])[-20:]
        request.session['assistant_history'] = history

        if turn['clarification_context']:
            request.session['assistant_clarification'] = turn['clarification_context']
        else:
            request.session.pop('assistant_clarification', None)

        request.session.modified = True

        save_turn(
            session,
            message,
            turn['response']['message'],
            response_type=turn['response']['type'],
            response_data=turn['response'].get('data'),
            intent=turn.get('intent') or '',
            pending_context=turn.get('clarification_context'),
        )

        return Response(
            {
                'message': turn['response']['message'],
                'type': turn['response']['type'],
                'data': turn['response'].get('data'),
                'intent': turn.get('intent'),
                'clarification_context': turn.get('clarification_context'),
                'session_id': session.id,
            }
        )


class AssistantResetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.session.pop('assistant_history', None)
        request.session.pop('assistant_clarification', None)
        session = start_new_session(request.user)
        return Response({'ok': True, 'session_id': session.id})


class AssistantSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'sessions': list_sessions(request.user)})


class AssistantExportView(APIView):
    """Export a structured assistant result as CSV."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        response_type = request.data.get('type') or ''
        data = request.data.get('data')
        if not response_type or not data:
            return Response(
                {'error': 'type and data are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_text = result_to_csv(response_type, data)
        if not csv_text.strip():
            return Response(
                {'error': 'Nothing to export for this result type'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename = f'soupsnacks-{response_type}.csv'
        response = HttpResponse(csv_text, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class AssistantTranscribeView(APIView):
    """Transcribe microphone audio via Whisper (bypasses browser Speech API)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        audio = request.FILES.get('audio')
        if not audio:
            return Response({'error': 'audio file is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not getattr(settings, 'OPENAI_API_KEY', ''):
            return Response(
                {'error': 'Voice transcription is not configured (OPENAI_API_KEY missing)'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        content_type = audio.content_type or 'audio/webm'
        filename = audio.name or 'recording.webm'
        text = transcribe_audio(audio.read(), filename=filename, content_type=content_type)

        if not text:
            return Response(
                {'error': 'Could not transcribe audio. Try speaking again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({'text': text})
