from django.contrib import admin
from .models import (
    Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate,
    Category, Review, Coupon, Wishlist # <--- CORREÇÃO: Removido 'ProductCategory'
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('owner',)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj:
            ro.append('owner')
        return ro


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('sku', 'color', 'size', 'model', 'stock', 'price', 'is_active')
    # <--- CORREÇÃO: Removido 'autocomplete_fields' de 'product' (desnecessário em inline)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'total_stock', 'is_active', 'created_at')
    list_filter = ('store', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'total_stock')
    inlines = [ProductVariantInline]
    list_select_related = ('store',)
    # <--- MELHORIA: Adicionado filtro horizontal para o campo 'categories'
    filter_horizontal = ('categories',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'model', 'stock', 'price', 'is_active')
    list_filter = ('product__store', 'color', 'size', 'is_active')
    search_fields = ('sku', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('product',)
    autocomplete_fields = ('product',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # <--- CORREÇÃO: 'get_subtotal' é um método, não um campo. Deve ir apenas em readonly_fields.
    fields = ('variant', 'quantity', 'unit_price')
    readonly_fields = ('unit_price', 'get_subtotal')
    autocomplete_fields = ('variant',)

    # Adiciona 'get_subtotal' à exibição
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


class OrderStatusUpdateInline(admin.TabularInline):
    model = OrderStatusUpdate
    extra = 0
    readonly_fields = ('status', 'note', 'is_automatic', 'created_at')
    can_delete = False
    # Não permitir adicionar novos status por aqui (deve ser via actions)
    can_add = False 


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('total_amount', 'paid_at', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusUpdateInline]
    actions = ['action_mark_out_for_delivery', 'action_mark_delivered', 'action_mark_cancelled', 'action_mark_cod_paid']
    list_select_related = ('store',)

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
        count = 0
        for order in queryset.filter(payment_method='cod', payment_status='pending'):
            order.mark_cod_paid()
            count += 1
        self.message_user(request, f"{count} pedidos COD marcados como pagos.")
    action_mark_cod_paid.short_description = 'Marcar COD como pago'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    # <--- MELHORIA: Auto-preencher o slug a partir do nome
    prepopulated_fields = {'slug': ('name',)}


# <--- CORREÇÃO: Removido 'ProductCategoryAdmin' pois o model foi excluído
# (agora é um ManyToManyField direto em Product)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('product__name', 'user__username')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('product', 'user') # Adicionado autocomplete


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # <--- CORREÇÃO: Campos não existiam ('discount_percent', 'active', 'valid_to')
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_until', 'usage_count')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    autocomplete_fields = ('user', 'product')