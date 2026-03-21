from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('soups', 'Soups'),
        ('snacks', 'Snacks'),
        ('sweets', 'Sweets'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('pickle', 'Pickle'),
        ('combos', 'Combos'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Product name (e.g., Tomato Soup 250ml)'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text='Product category'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Product description'
    )
    unit = models.CharField(
        max_length=50,
        help_text='Unit size (e.g., 250ml, 500ml, 1 plate, 1 box)'
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Selling price per unit'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Active products can be offered'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]
        unique_together = [['name', 'unit']]  # Same product, different sizes
    
    def __str__(self):
        return f"{self.name} ({self.unit})"
    
    @property
    def unit_cost(self):
        """Calculate total cost from all cost components"""
        total = self.cost_components.aggregate(
            total=models.Sum('total_cost')
        )['total']
        return total or Decimal('0.00')
    
    @property
    def unit_profit(self):
        """Calculate profit per unit"""
        return self.selling_price - self.unit_cost
    
    @property
    def margin_percent(self):
        """Calculate profit margin percentage"""
        if self.selling_price > 0:
            return (self.unit_profit / self.selling_price) * 100
        return Decimal('0.00')
    
    @property
    def status(self):
        return "Active" if self.is_active else "Inactive"


class ProductCostComponent(models.Model):
    ITEM_TYPE_CHOICES = [
        ('ingredient', 'Ingredient'),
        ('labor', 'Labor'),
        ('fuel', 'Fuel'),
        ('packaging', 'Packaging'),
        ('transport', 'Transport'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cost_components',
        help_text='Product this cost belongs to'
    )
    item_name = models.CharField(
        max_length=200,
        help_text='Name of cost item (e.g., Tomatoes, Chef time, Gas)'
    )
    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES,
        help_text='Type of cost component'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text='Quantity used per unit'
    )
    unit_of_measure = models.CharField(
        max_length=50,
        help_text='Unit (e.g., kg, liters, hours, pieces)'
    )
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Cost per unit of measure'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text='Auto-calculated: quantity × cost_per_unit'
    )
    
    class Meta:
        ordering = ['item_type', 'item_name']
        verbose_name = 'Product Cost Component'
        verbose_name_plural = 'Product Cost Components'
    
    def __str__(self):
        return f"{self.product.name} - {self.item_name} ({self.item_type})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total_cost before saving"""
        self.total_cost = self.quantity * self.cost_per_unit
        super().save(*args, **kwargs)
