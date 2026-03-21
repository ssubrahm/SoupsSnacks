from rest_framework import serializers
from .models import Product, ProductCostComponent


class ProductCostComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCostComponent
        fields = [
            'id', 'item_name', 'item_type', 'quantity', 
            'unit_of_measure', 'cost_per_unit', 'total_cost'
        ]
        read_only_fields = ['id', 'total_cost']
    
    def validate(self, data):
        # Ensure positive values
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError({'quantity': 'Quantity must be greater than 0'})
        if data.get('cost_per_unit', 0) <= 0:
            raise serializers.ValidationError({'cost_per_unit': 'Cost per unit must be greater than 0'})
        return data


class ProductSerializer(serializers.ModelSerializer):
    cost_components = ProductCostComponentSerializer(many=True, read_only=True)
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unit_profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    margin_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'unit', 'selling_price',
            'is_active', 'status', 'notes', 'created_at', 'updated_at',
            'cost_components', 'unit_cost', 'unit_profit', 'margin_percent'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 
                           'unit_cost', 'unit_profit', 'margin_percent']
    
    def validate_selling_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Selling price must be greater than 0')
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unit_profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    margin_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    status = serializers.ReadOnlyField()
    component_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'unit', 'selling_price',
            'is_active', 'status', 'unit_cost', 'unit_profit', 
            'margin_percent', 'component_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status', 
                           'unit_cost', 'unit_profit', 'margin_percent']
    
    def get_component_count(self, obj):
        return obj.cost_components.count()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products with cost components"""
    cost_components = ProductCostComponentSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'unit', 'selling_price',
            'is_active', 'notes', 'cost_components'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        cost_components_data = validated_data.pop('cost_components', [])
        product = Product.objects.create(**validated_data)
        
        for component_data in cost_components_data:
            ProductCostComponent.objects.create(product=product, **component_data)
        
        return product
    
    def update(self, instance, validated_data):
        cost_components_data = validated_data.pop('cost_components', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If cost_components provided, replace all existing components
        if cost_components_data is not None:
            instance.cost_components.all().delete()
            for component_data in cost_components_data:
                ProductCostComponent.objects.create(product=instance, **component_data)
        
        return instance
