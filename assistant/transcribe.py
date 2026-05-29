"""Transcribe audio via OpenAI Whisper (works when browser Speech API fails)."""

from __future__ import annotations

import json
import os
import uuid
import urllib.error
import urllib.request

from django.conf import settings


def transcribe_audio(file_bytes: bytes, filename: str = 'audio.webm', content_type: str = 'audio/webm') -> str | None:
    """
    Send audio to OpenAI Whisper and return transcript text.
    Returns None if API unavailable or request fails.
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    if not api_key or not file_bytes:
        return None

    base_url = getattr(settings, 'OPENAI_BASE_URL', None) or os.getenv(
        'OPENAI_BASE_URL', 'https://api.openai.com/v1'
    )
    model = os.getenv('OPENAI_WHISPER_MODEL', 'whisper-1')

    boundary = f'----SoupsSnacks{uuid.uuid4().hex}'
    body = bytearray()

    def add_field(name: str, value: str) -> None:
        body.extend(f'--{boundary}\r\n'.encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(f'{value}\r\n'.encode())

    def add_file(name: str, fname: str, data: bytes, mime: str) -> None:
        body.extend(f'--{boundary}\r\n'.encode())
        body.extend(
            f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
        )
        body.extend(f'Content-Type: {mime}\r\n\r\n'.encode())
        body.extend(data)
        body.extend(b'\r\n')

    add_field('model', model)
    add_field('language', 'en')
    add_file('file', filename, file_bytes, content_type)
    body.extend(f'--{boundary}--\r\n'.encode())

    req = urllib.request.Request(
        f'{base_url.rstrip("/")}/audio/transcriptions',
        data=bytes(body),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': f'multipart/form-data; boundary={boundary}',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        text = (payload.get('text') or '').strip()
        return text or None
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError, OSError):
        return None
