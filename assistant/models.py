from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    """Persisted Ask chat session per user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistant_sessions',
    )
    title = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        label = self.title or f'Session {self.id}'
        return f'{label} ({self.user})'


class ChatMessage(models.Model):
    """Single turn in an Ask chat session."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    response_type = models.CharField(max_length=32, blank=True, default='')
    response_data = models.JSONField(null=True, blank=True)
    intent = models.CharField(max_length=64, blank=True, default='')
    pending_context = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        preview = (self.content or '')[:48]
        return f'{self.role}: {preview}'
