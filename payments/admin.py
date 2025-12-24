from django.contrib import admin
from .models import Item, Order, Discount, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_price_in_dollars', 'currency', 'description')
    list_filter = ('currency',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_display_total', 'get_currency', 'created_at', 'items_count')
    list_filter = ('created_at', 'discount', 'tax')
    filter_horizontal = ('items',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items Count"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'currency')
    list_filter = ('discount_type', 'currency')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_type', 'value', 'currency')
    list_filter = ('tax_type', 'currency')
    search_fields = ('name', 'description')
    ordering = ('name',)
