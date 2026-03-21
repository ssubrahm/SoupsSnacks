from django.contrib import admin
from .models import Product, ProductCostComponent


class ProductCostComponentInline(admin.TabularInline):
    model = ProductCostComponent
    extra = 1
    readonly_fields = ['total_cost']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'category', 'selling_price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductCostComponentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'unit', 'description')
        }),
        ('Pricing', {
            'fields': ('selling_price',)
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductCostComponent)
class ProductCostComponentAdmin(admin.ModelAdmin):
    list_display = ['product', 'item_name', 'item_type', 'quantity', 'unit_of_measure', 'cost_per_unit', 'total_cost']
    list_filter = ['item_type', 'product__category']
    search_fields = ['item_name', 'product__name']
    readonly_fields = ['total_cost']
