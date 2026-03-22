from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from accounts.permissions import IsOperator
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderCreateUpdateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order management - Accessible by Admin and Operator
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrderCreateUpdateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        queryset = Order.objects.select_related('customer').prefetch_related('items__product')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by order type
        order_type = self.request.query_params.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Filter by fulfillment date
        fulfillment_date = self.request.query_params.get('fulfillment_date')
        if fulfillment_date:
            queryset = queryset.filter(fulfillment_date=fulfillment_date)
        
        # Search by order number or customer name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__mobile__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        by_status = {}
        for status_choice in Order.STATUS_CHOICES:
            status_code = status_choice[0]
            by_status[status_code] = queryset.filter(status=status_code).count()
        
        by_payment = {}
        for payment_choice in Order.PAYMENT_STATUS_CHOICES:
            payment_code = payment_choice[0]
            by_payment[payment_code] = queryset.filter(payment_status=payment_code).count()
        
        # Revenue stats
        total_revenue = sum(order.total_revenue for order in queryset)
        total_profit = sum(order.total_profit for order in queryset)
        
        return Response({
            'total': total,
            'by_status': by_status,
            'by_payment': by_payment,
            'total_revenue': float(total_revenue),
            'total_profit': float(total_profit),
        })
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_payment_status(self, request, pk=None):
        """Change payment status"""
        order = self.get_object()
        new_status = request.data.get('payment_status')
        
        if new_status not in dict(Order.PAYMENT_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid payment status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        today = datetime.now().date()
        queryset = self.get_queryset().filter(
            Q(order_date=today) | Q(fulfillment_date=today)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders (not completed or cancelled)"""
        queryset = self.get_queryset().exclude(
            status__in=['completed', 'cancelled']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
