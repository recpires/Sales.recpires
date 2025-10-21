from django.contrib import admin
from .models import Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('sku', 'color', 'size', 'model', 'stock', 'price', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'total_stock', 'is_active', 'created_at')
    list_filter = ('store', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'total_stock')
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'model', 'stock', 'price', 'is_active')
    list_filter = ('product__store', 'color', 'size', 'is_active')
    search_fields = ('sku', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'get_subtotal')
    fields = ('variant', 'quantity', 'unit_price', 'get_subtotal')


class OrderStatusUpdateInline(admin.TabularInline):
    model = OrderStatusUpdate
    extra = 0
    readonly_fields = ('status', 'note', 'is_automatic', 'created_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('total_amount', 'paid_at', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusUpdateInline]
    actions = ['action_mark_out_for_delivery', 'action_mark_delivered', 'action_mark_cancelled', 'action_mark_cod_paid']

    def action_mark_out_for_delivery(self, request, queryset):
        for order in queryset:
            order.set_status('out_for_delivery', note='Atualizado via Admin', automatic=False)
    action_mark_out_for_delivery.short_description = 'Marcar como "Saiu para entrega"'

    def action_mark_delivered(self, request, queryset):
        for order in queryset:
            order.set_status('delivered', note='Atualizado via Admin', automatic=False)
    action_mark_delivered.short_description = 'Marcar como "Entregue"'

    def action_mark_cancelled(self, request, queryset):
        for order in queryset:
            order.set_status('cancelled', note='Atualizado via Admin', automatic=False)
    action_mark_cancelled.short_description = 'Marcar como "Cancelado"'

    def action_mark_cod_paid(self, request, queryset):
        for order in queryset.filter(payment_method='cod'):
            order.mark_cod_paid()
    action_mark_cod_paid.short_description = 'Marcar COD como pago'
