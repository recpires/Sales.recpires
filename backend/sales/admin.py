from django.contrib import admin
from .models import Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_active',)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('store', 'is_active', 'color', 'size')
    search_fields = ('name', 'sku')
    inlines = [ProductVariantInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

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
        for order in queryset:
            if order.payment_method == 'cod':
                order.mark_cod_paid()
    action_mark_cod_paid.short_description = 'Marcar COD como pago'
