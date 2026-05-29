from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from accounts.permissions import IsOperator
from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer, PaymentListSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Payment management - Accessible by Admin and Operator
    """
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('order', 'order__customer')
        
        # Filter by order
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by payment method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method=method)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        queryset = self.get_queryset()
        
        total_payments = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        by_method = {}
        for method_choice in Payment.PAYMENT_METHOD_CHOICES:
            method_code = method_choice[0]
            count = queryset.filter(method=method_code).count()
            amount = queryset.filter(method=method_code).aggregate(total=Sum('amount'))['total'] or 0
            by_method[method_code] = {
                'count': count,
                'amount': float(amount)
            }
        
        return Response({
            'total_payments': total_payments,
            'total_amount': float(total_amount),
            'by_method': by_method,
        })
    
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """Get payment summary for a specific order"""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {'error': 'order_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payments = order.payments.all()
        total_paid = sum(p.amount for p in payments)
        outstanding = order.total_revenue - total_paid
        
        return Response({
            'order_id': order.id,
            'order_number': order.order_number,
            'order_total': float(order.total_revenue),
            'total_paid': float(total_paid),
            'outstanding': float(outstanding),
            'payment_status': order.payment_status,
            'payment_count': payments.count(),
        })
