from django.db import models
from django.utils import timezone
from customers.models import Customer
from catalog.models import Product


class Order(models.Model):
    """Customer order with multiple line items"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Auto-generated order number'
    )
    order_date = models.DateField(
        default=timezone.now,
        db_index=True,
        help_text='Date order was placed'
    )
    fulfillment_date = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        help_text='Date order should be fulfilled'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPE_CHOICES,
        default='delivery'
    )
    delivery_address = models.TextField(
        blank=True,
        null=True,
        help_text='Delivery address if different from customer default'
    )
    delivery_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Delivery instructions'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal order notes'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date', '-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    @property
    def total_revenue(self):
        """Total revenue from all line items"""
        return sum(item.line_total for item in self.items.all())
    
    @property
    def total_cost(self):
        """Total cost from all line items"""
        return sum(item.line_cost for item in self.items.all())
    
    @property
    def total_profit(self):
        """Total profit (revenue - cost)"""
        return self.total_revenue - self.total_cost
    
    @property
    def margin_percent(self):
        """Profit margin percentage"""
        if self.total_revenue == 0:
            return 0
        return (self.total_profit / self.total_revenue) * 100
    
    @property
    def item_count(self):
        """Total number of line items"""
        return self.items.count()
    
    @property
    def total_quantity(self):
        """Total quantity of all items"""
        return sum(item.quantity for item in self.items.all())
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number in format: ORD-YYYYMMDD-XXXX"""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        prefix = f"ORD-{date_str}-"
        
        # Find last order number for today
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('order_number').last()
        
        if last_order:
            last_seq = int(last_order.order_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}{new_seq:04d}"


class OrderItem(models.Model):
    """Individual line item in an order"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Selling price at time of order'
    )
    unit_cost_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Product cost at time of order (snapshot)'
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Display order in the order'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.order.order_number}"
    
    @property
    def line_total(self):
        """Total price for this line (quantity × unit_price)"""
        return self.quantity * self.unit_price
    
    @property
    def line_cost(self):
        """Total cost for this line (quantity × unit_cost_snapshot)"""
        return self.quantity * self.unit_cost_snapshot
    
    @property
    def line_profit(self):
        """Profit for this line"""
        return self.line_total - self.line_cost
    
    @property
    def line_margin_percent(self):
        """Margin percentage for this line"""
        if self.line_total == 0:
            return 0
        return (self.line_profit / self.line_total) * 100
