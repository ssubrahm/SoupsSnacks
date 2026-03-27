from django.urls import path
from .views import ImportPreviewView, ImportConfirmView, ImportHistoryView, ImportTemplateView

urlpatterns = [
    path('preview/', ImportPreviewView.as_view(), name='import-preview'),
    path('confirm/', ImportConfirmView.as_view(), name='import-confirm'),
    path('history/', ImportHistoryView.as_view(), name='import-history'),
    path('template/<str:import_type>/', ImportTemplateView.as_view(), name='import-template'),
]
