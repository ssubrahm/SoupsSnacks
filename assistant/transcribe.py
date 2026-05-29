"""Transcribe audio via OpenAI Whisper (works when browser Speech API fails)."""

from __future__ import annotations

import json
import os
import uuid
import urllib.error
import urllib.request

from django.conf import settings

# Whisper accepts common browser capture formats; normalize Safari mp4 uploads.
MIME_TO_EXT = {
    'audio/webm': 'webm',
    'audio/webm;codecs=opus': 'webm',
    'audio/mp4': 'm4a',
    'audio/m4a': 'm4a',
    'audio/x-m4a': 'm4a',
    'audio/ogg': 'ogg',
    'audio/ogg;codecs=opus': 'ogg',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/mpeg': 'mp3',
    'audio/mp3': 'mp3',
}


def normalize_audio_upload(filename: str, content_type: str) -> tuple[str, str]:
    """Ensure Whisper receives a filename extension that matches the audio bytes."""
    mime = (content_type or 'audio/webm').split(';')[0].strip().lower()
    ext = MIME_TO_EXT.get(mime) or MIME_TO_EXT.get(content_type.lower() if content_type else '')
    if not ext and '.' in filename:
        ext = filename.rsplit('.', 1)[-1].lower()
    if not ext:
        ext = 'webm'
    if not filename or '.' not in filename:
        filename = f'recording.{ext}'
    elif not filename.lower().endswith(f'.{ext}'):
        filename = f'recording.{ext}'
    normalized_mime = content_type or mime or 'audio/webm'
    return filename, normalized_mime


def transcribe_audio(file_bytes: bytes, filename: str = 'audio.webm', content_type: str = 'audio/webm') -> str | None:
    """
    Send audio to OpenAI Whisper and return transcript text.
    Returns None if API unavailable or request fails.
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    if not api_key or not file_bytes:
        return None

    filename, content_type = normalize_audio_upload(filename, content_type)

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
