from rest_framework import serializers
from .models import ImportLog


class ImportLogSerializer(serializers.ModelSerializer):
    imported_by_name = serializers.CharField(source='imported_by.username', read_only=True)
    
    class Meta:
        model = ImportLog
        fields = [
            'id', 'import_type', 'file_name', 'status',
            'total_rows', 'successful_rows', 'failed_rows',
            'errors', 'imported_ids', 'imported_by', 'imported_by_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class ImportPreviewSerializer(serializers.Serializer):
    """Serializer for import preview response"""
    headers = serializers.ListField(child=serializers.CharField())
    rows = serializers.ListField()
    total_rows = serializers.IntegerField()
    valid_rows = serializers.IntegerField()
    invalid_rows = serializers.IntegerField()
    errors = serializers.ListField()
    preview_data = serializers.ListField()
