from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import IsOperator
from .models import Customer
from .serializers import CustomerSerializer, CustomerListSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer management - Accessible by Admin and Operator
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsOperator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'mobile', 'email', 'apartment_name', 'block']
    ordering_fields = ['name', 'apartment_name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer
    
    def get_queryset(self):
        queryset = Customer.objects.all()
        
        # Filter by active/inactive status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by apartment
        apartment = self.request.query_params.get('apartment_name', None)
        if apartment:
            queryset = queryset.filter(apartment_name__iexact=apartment)
        
        # Filter by block
        block = self.request.query_params.get('block', None)
        if block:
            queryset = queryset.filter(block__iexact=block)
        
        # Search by name, mobile, email, apartment, or block
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(mobile__icontains=search) |
                Q(email__icontains=search) |
                Q(apartment_name__icontains=search) |
                Q(block__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle customer active status"""
        customer = self.get_object()
        customer.is_active = not customer.is_active
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get customer statistics"""
        total = Customer.objects.count()
        active = Customer.objects.filter(is_active=True).count()
        inactive = total - active
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive
        })
    
    @action(detail=False, methods=['get'])
    def apartments(self, request):
        """Get list of unique apartment names"""
        apartments = Customer.objects.filter(
            apartment_name__isnull=False
        ).exclude(
            apartment_name=''
        ).values_list('apartment_name', flat=True).distinct().order_by('apartment_name')
        
        return Response(list(apartments))
    
    @action(detail=False, methods=['get'])
    def blocks(self, request):
        """Get list of unique blocks"""
        apartment = request.query_params.get('apartment_name', None)
        
        queryset = Customer.objects.filter(
            block__isnull=False
        ).exclude(block='')
        
        if apartment:
            queryset = queryset.filter(apartment_name__iexact=apartment)
        
        blocks = queryset.values_list('block', flat=True).distinct().order_by('block')
        
        return Response(list(blocks))
