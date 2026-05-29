from django.urls import path
from .views import (
    GoogleSheetConfigListView,
    GoogleSheetConfigDetailView,
    GoogleSheetTestConnectionView,
    GoogleSheetSyncView,
    GoogleSheetSyncHistoryView,
    GoogleSheetProductsView,
)

urlpatterns = [
    # Google Sheets Integration
    path('google-sheets/', GoogleSheetConfigListView.as_view(), name='google-sheets-list'),
    path('google-sheets/<int:pk>/', GoogleSheetConfigDetailView.as_view(), name='google-sheets-detail'),
    path('google-sheets/test-connection/', GoogleSheetTestConnectionView.as_view(), name='google-sheets-test'),
    path('google-sheets/<int:pk>/sync/', GoogleSheetSyncView.as_view(), name='google-sheets-sync'),
    path('google-sheets/sync-history/', GoogleSheetSyncHistoryView.as_view(), name='google-sheets-history-all'),
    path('google-sheets/<int:pk>/sync-history/', GoogleSheetSyncHistoryView.as_view(), name='google-sheets-history'),
    path('google-sheets/products/', GoogleSheetProductsView.as_view(), name='google-sheets-products'),
]
