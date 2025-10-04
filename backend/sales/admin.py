from django.contrib import admin
from .models import Product, Order, OrderItem, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'owner__username', 'email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'sku', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'store', 'created_at']
    search_fields = ['name', 'sku', 'description', 'store__name']
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price']
    readonly_fields = ['unit_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'customer_name', 'customer_email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'store', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'id', 'store__name']
    list_editable = ['status']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Store Information', {
            'fields': ('store',)
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'shipping_address')
        }),
        ('Order Details', {
            'fields': ('status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'get_subtotal']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['unit_price']

    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'
