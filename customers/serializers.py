from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'mobile', 'email', 'apartment_name', 'block', 'address', 
            'notes', 'is_active', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def validate_mobile(self, value):
        # Clean mobile number
        cleaned = value.strip().replace(' ', '').replace('-', '')
        return cleaned


class CustomerListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'mobile', 'email', 'apartment_name', 'block', 'is_active', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'status']
