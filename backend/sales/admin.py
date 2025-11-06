from django.contrib import admin
from .models import (
    Store, Product, ProductVariant, Category, Coupon,
    Order, OrderItem, OrderStatusUpdate, 
    Supplier, PurchaseOrder, PurchaseOrderItem # Novos modelos
)

# --------------------
# Base Inlines
# --------------------

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('variant',) # Usa raw_id_fields para Variants
    extra = 1

class OrderStatusUpdateInline(admin.TabularInline):
    model = OrderStatusUpdate
    extra = 0
    readonly_fields = ('timestamp',)

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    raw_id_fields = ('variant',) # Usa raw_id_fields para Variants
    extra = 1
    fields = ('variant', 'ordered_quantity', 'received_quantity', 'unit_cost', 'total_cost')
    readonly_fields = ('total_cost',)


# --------------------
# Admin Models
# --------------------

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'slug', 'currency', 'created_at')
    search_fields = ('name', 'user__username')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'slug')
    list_filter = ('store',)
    search_fields = ('name', 'store__name')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        # Permite apenas que usuários vejam categorias das suas lojas
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'category', 'is_active', 'created_at')
    list_filter = ('store', 'category', 'is_active')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)
        
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'price', 'stock_quantity', 'color', 'size')
    list_filter = ('product__store', 'color', 'size')
    search_fields = ('sku', 'product__name', 'product__store__name')
    raw_id_fields = ('product',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(product__store__user=request.user)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('store', 'status', 'payment_method')
    search_fields = ('id', 'user__username', 'store__name')
    inlines = [OrderItemInline, OrderStatusUpdateInline]
    readonly_fields = ('total_amount', 'discount_amount', 'created_at', 'updated_at', 'paid_at')
    fieldsets = (
        (None, {
            'fields': ('store', 'user', 'status', 'coupon', 'payment_method', 'paid_at')
        }),
        ('Valores', {
            'fields': ('total_amount', 'discount_amount')
        }),
        ('Entrega', {
            'fields': ('shipping_address',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'store', 'type', 'value', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('store', 'type', 'is_active')
    search_fields = ('code', 'store__name')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)

# --------------------
# NOVOS ADMINS PARA PO
# --------------------

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'contact_name', 'email', 'phone')
    list_filter = ('store',)
    search_fields = ('name', 'email', 'store__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'supplier', 'status', 'order_date', 'total_cost')
    list_filter = ('store', 'status', 'supplier')
    search_fields = ('id', 'supplier__name', 'store__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('order_date', 'total_cost')
    actions = ['mark_as_received_full']

    def mark_as_received_full(self, request, queryset):
        # Ação personalizada para marcar como 'RECEIVED_FULL' e atualizar estoque.
        # Esta lógica deve ser replicada no Viewset para a API.
        
        for po in queryset:
            if po.status != 'RECEIVED_FULL':
                po.status = 'RECEIVED_FULL'
                po.save()
                
                # Lógica de atualização de estoque
                for item in po.po_items.all():
                    # Se a quantidade recebida for menor que a pedida, ajustamos para a pedida para Full.
                    # Se já foi recebido algo antes (received_quantity > 0), apenas atualizamos a diferença.
                    if item.received_quantity < item.ordered_quantity:
                        quantity_to_add = item.ordered_quantity - item.received_quantity
                        item.variant.stock_quantity += quantity_to_add
                        item.variant.save()
                        item.received_quantity = item.ordered_quantity
                        item.save()
                        
        self.message_user(request, f"{queryset.count()} Pedido(s) de Compra(s) marcado(s) como Recebido Totalmente e estoque atualizado.")
    
    mark_as_received_full.short_description = _("Marcar como Recebido Totalmente e Atualizar Estoque")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__user=request.user)