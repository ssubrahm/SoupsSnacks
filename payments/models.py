from django.db import models
from django.core.exceptions import ValidationError
from orders.models import Order


class Payment(models.Model):
    """Payment tracking for orders"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('other', 'Other'),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    payment_date = models.DateField(
        help_text='Date payment was received'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Payment amount received'
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='upi'
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='UPI transaction ID, check number, etc.'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about this payment'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"₹{self.amount} for {self.order.order_number} on {self.payment_date}"
    
    def clean(self):
        """Validate payment amount"""
        if self.amount <= 0:
            raise ValidationError({'amount': 'Payment amount must be greater than 0'})
        
        # Check if total payments would exceed order total
        if self.order:
            current_total = sum(
                p.amount for p in self.order.payments.exclude(id=self.id) if p.amount
            )
            if self.amount:
                new_total = current_total + self.amount
                order_total = self.order.total_revenue
                
                # Allow slight overpayment (within 0.01) due to rounding
                if new_total > order_total + 0.01:
                    raise ValidationError({
                        'amount': f'Total payments (₹{new_total:.2f}) would exceed order total (₹{order_total:.2f}). Outstanding: ₹{order_total - current_total:.2f}'
                    })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Update order payment status after saving
        self.update_order_payment_status()
    
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        # Update order payment status after deletion
        self.update_order_payment_status_for_order(order)
    
    def update_order_payment_status(self):
        """Update order payment status based on total payments"""
        if self.order:
            self.update_order_payment_status_for_order(self.order)
    
    @staticmethod
    def update_order_payment_status_for_order(order):
        """Update payment status for a given order"""
        total_paid = sum(p.amount for p in order.payments.all())
        order_total = order.total_revenue
        
        if total_paid == 0:
            order.payment_status = 'pending'
        elif total_paid >= order_total:
            order.payment_status = 'paid'
        else:
            order.payment_status = 'partial'
        
        order.save()
