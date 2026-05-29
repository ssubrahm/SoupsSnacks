from rest_framework import serializers
from .models import DailyOffering, DailyOfferingItem
from catalog.serializers import ProductListSerializer


class DailyOfferingItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = DailyOfferingItem
        fields = [
            'id', 'product', 'product_details', 'available_quantity', 
            'display_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_available_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Available quantity cannot be negative')
        return value


class DailyOfferingSerializer(serializers.ModelSerializer):
    items = DailyOfferingItemSerializer(many=True, read_only=True)
    status = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyOffering
        fields = [
            'id', 'offering_date', 'notes', 'is_active', 'status',
            'item_count', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'item_count']


class DailyOfferingListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    status = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyOffering
        fields = [
            'id', 'offering_date', 'is_active', 'status',
            'item_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status', 'item_count']


class DailyOfferingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating offerings with items"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = DailyOffering
        fields = ['id', 'offering_date', 'notes', 'is_active', 'items']
        read_only_fields = ['id']
    
    def validate_items(self, value):
        """Validate items structure"""
        for item in value:
            if 'product' not in item:
                raise serializers.ValidationError('Each item must have a product ID')
            if not isinstance(item['product'], int):
                raise serializers.ValidationError('Product must be an integer ID')
            if 'available_quantity' in item and item['available_quantity'] is not None:
                if item['available_quantity'] < 0:
                    raise serializers.ValidationError('Available quantity cannot be negative')
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        offering = DailyOffering.objects.create(**validated_data)
        
        for idx, item_data in enumerate(items_data):
            DailyOfferingItem.objects.create(
                daily_offering=offering,
                product_id=item_data['product'],
                available_quantity=item_data.get('available_quantity'),
                display_order=item_data.get('display_order', idx)
            )
        
        return offering
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update offering fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If items provided, replace all existing items
        if items_data is not None:
            instance.items.all().delete()
            for idx, item_data in enumerate(items_data):
                DailyOfferingItem.objects.create(
                    daily_offering=instance,
                    product_id=item_data['product'],
                    available_quantity=item_data.get('available_quantity'),
                    display_order=item_data.get('display_order', idx)
                )
        
        return instance
