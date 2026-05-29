from django.urls import path

from .views import (
    AssistantChatView,
    AssistantExportView,
    AssistantResetView,
    AssistantSessionsView,
    AssistantTranscribeView,
)

urlpatterns = [
    path('chat/', AssistantChatView.as_view(), name='assistant-chat'),
    path('reset/', AssistantResetView.as_view(), name='assistant-reset'),
    path('sessions/', AssistantSessionsView.as_view(), name='assistant-sessions'),
    path('export/', AssistantExportView.as_view(), name='assistant-export'),
    path('transcribe/', AssistantTranscribeView.as_view(), name='assistant-transcribe'),
]
