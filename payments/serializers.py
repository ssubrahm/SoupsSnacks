from decimal import Decimal
from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderListSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order_details = OrderListSerializer(source='order', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_details', 'payment_date', 'amount',
            'method', 'reference', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Payment amount must be greater than 0')
        return value
    
    def validate(self, data):
        # Get order
        order = data.get('order')
        amount = data.get('amount')
        
        if order and amount:
            # Calculate current total (excluding this payment if updating)
            if self.instance:
                current_total = sum(
                    p.amount for p in order.payments.exclude(id=self.instance.id)
                )
            else:
                current_total = sum(p.amount for p in order.payments.all())
            
            new_total = current_total + amount
            order_total = order.total_revenue
            
            # Check for overpayment (allow 0.01 rounding tolerance)
            if new_total > order_total + Decimal('0.01'):
                outstanding = order_total - current_total
                raise serializers.ValidationError({
                    'amount': f'Total payments (₹{new_total:.2f}) would exceed order total (₹{order_total:.2f}). Outstanding: ₹{outstanding:.2f}'
                })
        
        return data


class PaymentListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_date', 'amount', 'method', 'reference', 'created_at']
        read_only_fields = ['id', 'created_at']
