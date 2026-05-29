from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'apartment_name', 'block', 'is_active', 'created_at']
    list_filter = ['is_active', 'apartment_name', 'block', 'created_at']
    search_fields = ['name', 'mobile', 'email', 'apartment_name', 'block']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'mobile', 'email')
        }),
        ('Location Details', {
            'fields': ('apartment_name', 'block', 'address')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
