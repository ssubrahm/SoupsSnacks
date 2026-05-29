from rest_framework import serializers
from .models import GoogleSheetConfig, GoogleSheetSyncLog


class GoogleSheetConfigSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    last_sync = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleSheetConfig
        fields = [
            'id', 'name', 'sheet_id', 'tab_name', 'field_mapping',
            'default_product_id', 'default_order_type', 'last_synced_row',
            'is_active', 'write_back_enabled', 'order_number_column',
            'status_column', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'last_sync'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_last_sync(self, obj):
        last_log = obj.sync_logs.first()
        if last_log:
            return {
                'id': last_log.id,
                'status': last_log.status,
                'rows_created': last_log.rows_created,
                'started_at': last_log.started_at
            }
        return None


class GoogleSheetSyncLogSerializer(serializers.ModelSerializer):
    config_name = serializers.CharField(source='config.name', read_only=True)
    synced_by_name = serializers.CharField(source='synced_by.username', read_only=True)
    
    class Meta:
        model = GoogleSheetSyncLog
        fields = [
            'id', 'config', 'config_name', 'status',
            'rows_processed', 'rows_created', 'rows_skipped', 'rows_failed',
            'errors', 'created_order_ids', 'started_at', 'completed_at',
            'synced_by', 'synced_by_name'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
