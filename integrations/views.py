from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.permissions import IsAdmin
from .models import GoogleSheetConfig, GoogleSheetSyncLog
from .serializers import GoogleSheetConfigSerializer, GoogleSheetSyncLogSerializer
from catalog.models import Product


class GoogleSheetConfigListView(APIView):
    """List and create Google Sheet configurations"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        configs = GoogleSheetConfig.objects.all()
        serializer = GoogleSheetConfigSerializer(configs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = GoogleSheetConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleSheetConfigDetailView(APIView):
    """Get, update, or delete a Google Sheet configuration"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, pk):
        try:
            config = GoogleSheetConfig.objects.get(pk=pk)
            serializer = GoogleSheetConfigSerializer(config)
            return Response(serializer.data)
        except GoogleSheetConfig.DoesNotExist:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            config = GoogleSheetConfig.objects.get(pk=pk)
            serializer = GoogleSheetConfigSerializer(config, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except GoogleSheetConfig.DoesNotExist:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            config = GoogleSheetConfig.objects.get(pk=pk)
            config.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GoogleSheetConfig.DoesNotExist:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)


class GoogleSheetTestConnectionView(APIView):
    """Test connection to a Google Sheet"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        sheet_id = request.data.get('sheet_id')
        tab_name = request.data.get('tab_name', 'Form Responses 1')
        
        if not sheet_id:
            return Response({'error': 'sheet_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .google_sheets_service import test_connection
            result = test_connection(sheet_id, tab_name)
            return Response(result)
        except ImportError as e:
            return Response({
                'success': False,
                'message': str(e),
                'headers': [],
                'row_count': 0
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e),
                'headers': [],
                'row_count': 0
            })


class GoogleSheetSyncView(APIView):
    """Trigger a sync for a Google Sheet configuration"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        try:
            config = GoogleSheetConfig.objects.get(pk=pk)
        except GoogleSheetConfig.DoesNotExist:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from .google_sheets_service import sync_google_sheet
            sync_log = sync_google_sheet(config.id, user=request.user)
            serializer = GoogleSheetSyncLogSerializer(sync_log)
            return Response(serializer.data)
        except ImportError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleSheetSyncHistoryView(APIView):
    """View sync history for a configuration or all"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, pk=None):
        if pk:
            logs = GoogleSheetSyncLog.objects.filter(config_id=pk)
        else:
            logs = GoogleSheetSyncLog.objects.all()
        
        logs = logs[:50]  # Limit to last 50
        serializer = GoogleSheetSyncLogSerializer(logs, many=True)
        return Response(serializer.data)


class GoogleSheetProductsView(APIView):
    """List products for dropdown in config"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        products = Product.objects.filter(is_active=True).values('id', 'name', 'unit', 'selling_price')
        return Response(list(products))
