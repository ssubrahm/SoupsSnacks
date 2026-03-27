from django.db import models
from django.conf import settings


class ImportLog(models.Model):
    """Log of all import operations"""
    
    IMPORT_TYPE_CHOICES = [
        ('customers', 'Customers'),
        ('products', 'Products'),
        ('orders', 'Orders'),
        ('payments', 'Payments'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    
    errors = models.JSONField(default=list, blank=True)
    imported_ids = models.JSONField(default=list, blank=True)
    
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='imports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Import Log'
        verbose_name_plural = 'Import Logs'
    
    def __str__(self):
        return f"{self.import_type} import - {self.file_name} ({self.status})"
