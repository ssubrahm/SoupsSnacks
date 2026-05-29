from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_date', 'amount', 'method', 'reference', 'created_at']
    list_filter = ['method', 'payment_date']
    search_fields = ['order__order_number', 'reference']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'payment_date'
