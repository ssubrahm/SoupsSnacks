from django.db import models
from django.conf import settings


class GoogleSheetConfig(models.Model):
    """Configuration for Google Sheets integration"""
    
    name = models.CharField(
        max_length=100,
        help_text='Friendly name for this integration (e.g., "Mango Pickle Orders")'
    )
    sheet_id = models.CharField(
        max_length=200,
        help_text='Google Sheet ID (from the URL)'
    )
    tab_name = models.CharField(
        max_length=100,
        default='Form Responses 1',
        help_text='Name of the tab/worksheet to read from'
    )
    
    # Field mappings (JSON) - maps sheet columns to our fields
    # Example: {"customer_name": "A", "mobile": "B", "product": "C", "quantity": "D"}
    field_mapping = models.JSONField(
        default=dict,
        help_text='Mapping of our fields to sheet columns'
    )
    
    # Default values for orders from this sheet
    default_product_id = models.IntegerField(
        null=True, blank=True,
        help_text='Default product ID if not specified in sheet'
    )
    default_order_type = models.CharField(
        max_length=20,
        default='delivery',
        help_text='Default order type'
    )
    
    # Sync settings
    last_synced_row = models.IntegerField(
        default=1,
        help_text='Last row number that was synced (header is row 1)'
    )
    is_active = models.BooleanField(default=True)
    
    # Write-back settings
    write_back_enabled = models.BooleanField(
        default=False,
        help_text='Write order number and status back to sheet'
    )
    order_number_column = models.CharField(
        max_length=10,
        blank=True,
        help_text='Column to write order number (e.g., "G")'
    )
    status_column = models.CharField(
        max_length=10,
        blank=True,
        help_text='Column to write order status (e.g., "H")'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='google_sheet_configs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Google Sheet Configuration'
        verbose_name_plural = 'Google Sheet Configurations'
    
    def __str__(self):
        return f"{self.name} ({self.sheet_id[:20]}...)"


class GoogleSheetSyncLog(models.Model):
    """Log of sync operations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    config = models.ForeignKey(
        GoogleSheetConfig,
        on_delete=models.CASCADE,
        related_name='sync_logs'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Sync results
    rows_processed = models.IntegerField(default=0)
    rows_created = models.IntegerField(default=0)
    rows_skipped = models.IntegerField(default=0)
    rows_failed = models.IntegerField(default=0)
    
    # Details
    errors = models.JSONField(default=list)
    created_order_ids = models.JSONField(default=list)
    
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    
    synced_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Google Sheet Sync Log'
        verbose_name_plural = 'Google Sheet Sync Logs'
    
    def __str__(self):
        return f"Sync {self.id} - {self.config.name} ({self.status})"


class GoogleSheetOrderRef(models.Model):
    """Tracks which sheet rows have been imported to prevent duplicates"""
    
    config = models.ForeignKey(
        GoogleSheetConfig,
        on_delete=models.CASCADE,
        related_name='order_refs'
    )
    sheet_row = models.IntegerField(help_text='Row number in the sheet')
    row_hash = models.CharField(
        max_length=64,
        help_text='Hash of row data for change detection'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='google_sheet_refs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['config', 'sheet_row']
        verbose_name = 'Google Sheet Order Reference'
        verbose_name_plural = 'Google Sheet Order References'
    
    def __str__(self):
        return f"Row {self.sheet_row} -> {self.order.order_number}"
