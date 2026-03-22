from rest_framework import serializers
from .models import Order, OrderItem
from customers.serializers import CustomerListSerializer
from catalog.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_margin_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'quantity', 'unit_price',
            'unit_cost_snapshot', 'display_order', 'line_total', 'line_cost',
            'line_profit', 'line_margin_percent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    
    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Unit price must be greater than 0')
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_details = CustomerListSerializer(source='customer', read_only=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    margin_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_date', 'fulfillment_date',
            'customer', 'customer_details', 'status', 'order_type',
            'delivery_address', 'delivery_notes', 'notes', 'payment_status',
            'items', 'total_revenue', 'total_cost', 'total_profit',
            'margin_percent', 'item_count', 'total_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    customer_details = CustomerListSerializer(source='customer', read_only=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_date', 'fulfillment_date',
            'customer', 'customer_details', 'status', 'order_type',
            'payment_status', 'total_revenue', 'total_profit',
            'item_count', 'total_quantity', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating orders with items"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_date', 'fulfillment_date', 'customer', 'status',
            'order_type', 'delivery_address', 'delivery_notes', 'notes',
            'payment_status', 'items'
        ]
        read_only_fields = ['id']
    
    def validate_items(self, value):
        """Validate items structure"""
        if not value:
            raise serializers.ValidationError('Order must have at least one item')
        
        for item in value:
            if 'product' not in item:
                raise serializers.ValidationError('Each item must have a product ID')
            if 'quantity' not in item:
                raise serializers.ValidationError('Each item must have a quantity')
            if 'unit_price' not in item:
                raise serializers.ValidationError('Each item must have a unit_price')
            if 'unit_cost_snapshot' not in item:
                raise serializers.ValidationError('Each item must have a unit_cost_snapshot')
            
            if item['quantity'] <= 0:
                raise serializers.ValidationError('Quantity must be greater than 0')
            if item['unit_price'] <= 0:
                raise serializers.ValidationError('Unit price must be greater than 0')
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for idx, item_data in enumerate(items_data):
            OrderItem.objects.create(
                order=order,
                product_id=item_data['product'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                unit_cost_snapshot=item_data['unit_cost_snapshot'],
                display_order=item_data.get('display_order', idx)
            )
        
        return order
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If items provided, replace all existing items
        if items_data is not None:
            instance.items.all().delete()
            for idx, item_data in enumerate(items_data):
                OrderItem.objects.create(
                    order=instance,
                    product_id=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    unit_cost_snapshot=item_data['unit_cost_snapshot'],
                    display_order=item_data.get('display_order', idx)
                )
        
        return instance
