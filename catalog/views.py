from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from accounts.permissions import IsAdmin, IsCook
from .models import Product, ProductCostComponent
from .serializers import (
    ProductSerializer, ProductListSerializer, 
    ProductCreateUpdateSerializer, ProductCostComponentSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product management - Accessible by Admin and Cook
    """
    queryset = Product.objects.all()
    permission_classes = [IsCook]  # Admin and Cook can access
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'category', 'selling_price', 'created_at']
    ordering = ['category', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by active/inactive
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle product active status"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get product statistics"""
        total = Product.objects.count()
        active = Product.objects.filter(is_active=True).count()
        inactive = total - active
        
        by_category = {}
        for category_code, category_name in Product.CATEGORY_CHOICES:
            count = Product.objects.filter(category=category_code).count()
            if count > 0:
                by_category[category_name] = count
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'by_category': by_category
        })
    
    @action(detail=True, methods=['post'])
    def add_cost_component(self, request, pk=None):
        """Add a cost component to a product"""
        product = self.get_object()
        serializer = ProductCostComponentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            # Return updated product
            product_serializer = ProductSerializer(product)
            return Response(product_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='remove_cost_component/(?P<component_id>[^/.]+)')
    def remove_cost_component(self, request, pk=None, component_id=None):
        """Remove a cost component from a product"""
        product = self.get_object()
        try:
            component = product.cost_components.get(id=component_id)
            component.delete()
            # Return updated product
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except ProductCostComponent.DoesNotExist:
            return Response(
                {'error': 'Cost component not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProductCostComponentViewSet(viewsets.ModelViewSet):
    """
    Cost component management
    """
    queryset = ProductCostComponent.objects.all()
    serializer_class = ProductCostComponentSerializer
    permission_classes = [IsCook]
    
    def get_queryset(self):
        queryset = ProductCostComponent.objects.all()
        
        # Filter by product
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by item type
        item_type = self.request.query_params.get('item_type', None)
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        return queryset
