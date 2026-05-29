from django.db import models
from catalog.models import Product


class DailyOffering(models.Model):
    """Daily menu offering for a specific date"""
    offering_date = models.DateField(
        unique=True,
        db_index=True,
        help_text='Date for this offering'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notes about this day\'s offering'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this offering is active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-offering_date']
        verbose_name = 'Daily Offering'
        verbose_name_plural = 'Daily Offerings'
    
    def __str__(self):
        return f"Offering for {self.offering_date}"
    
    @property
    def status(self):
        return "Active" if self.is_active else "Inactive"
    
    @property
    def item_count(self):
        return self.items.count()


class DailyOfferingItem(models.Model):
    """Individual product in a daily offering"""
    daily_offering = models.ForeignKey(
        DailyOffering,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    available_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Optional: Maximum quantity available for this product'
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Display order in the offering'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', 'id']
        unique_together = ['daily_offering', 'product']
        verbose_name = 'Daily Offering Item'
        verbose_name_plural = 'Daily Offering Items'
    
    def __str__(self):
        return f"{self.product.name} on {self.daily_offering.offering_date}"
