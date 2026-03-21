from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Customer full name'
    )
    mobile = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be 9-15 digits. Format: +919876543210 or 9876543210'
            )
        ],
        help_text='Mobile number with country code (optional)'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text='Customer email address'
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Full address'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about the customer'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Active customers can place orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['mobile']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.mobile})"
    
    @property
    def status(self):
        return "Active" if self.is_active else "Inactive"
