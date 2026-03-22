from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'unit_cost_snapshot', 'display_order']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'fulfillment_date', 
                    'status', 'payment_status', 'total_revenue', 'total_profit']
    list_filter = ['status', 'payment_status', 'order_type', 'order_date']
    search_fields = ['order_number', 'customer__name', 'customer__mobile']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 
                    'unit_cost_snapshot', 'line_total', 'line_profit']
    list_filter = ['order__order_date', 'product']
    search_fields = ['order__order_number', 'product__name']
