from django.contrib import admin
from .models import DailyOffering, DailyOfferingItem


class DailyOfferingItemInline(admin.TabularInline):
    model = DailyOfferingItem
    extra = 1


@admin.register(DailyOffering)
class DailyOfferingAdmin(admin.ModelAdmin):
    list_display = ['offering_date', 'item_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'offering_date']
    search_fields = ['notes']
    inlines = [DailyOfferingItemInline]


@admin.register(DailyOfferingItem)
class DailyOfferingItemAdmin(admin.ModelAdmin):
    list_display = ['daily_offering', 'product', 'available_quantity', 'display_order']
    list_filter = ['daily_offering__offering_date']
    search_fields = ['product__name']
