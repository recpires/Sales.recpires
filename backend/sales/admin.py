from django.contrib import admin, messages
from django.db import transaction
from django.db.utils import IntegrityError
from .models import Product, Order, OrderItem, Store, ProductVariant


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
    actions = ['create_variants_for_selected']

    def create_variants_for_selected(self, request, queryset):
        """Admin action: create a default variant for each selected product that has no variants."""
        created = 0
        skipped = 0
        failed = 0

        for p in queryset:
            if p.variants.exists():
                skipped += 1
                continue

            sku = p.sku if p.sku else f"PROD-{p.id}"
            if ProductVariant.objects.filter(sku=sku).exists():
                sku = f"{sku}-{p.id}"

            try:
                with transaction.atomic():
                    ProductVariant.objects.create(
                        product=p,
                        sku=sku,
                        price=p.price,
                        color=p.color if p.color else None,
                        size=p.size if p.size else None,
                        stock=p.stock,
                        image=p.image,
                        is_active=p.is_active,
                    )
                    created += 1
            except IntegrityError:
                failed += 1

        msgs = []
        if created:
            msgs.append(f"Created {created} variants.")
        if skipped:
            msgs.append(f"Skipped {skipped} products that already had variants.")
        if failed:
            msgs.append(f"Failed to create {failed} variants due to errors.")

        messages.info(request, ' '.join(msgs) if msgs else 'No products processed.')

    create_variants_for_selected.short_description = 'Create variants for selected products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'variant', 'quantity', 'unit_price']
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
    list_display = ['order', 'product', 'variant', 'quantity', 'unit_price', 'get_subtotal']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name', 'variant__sku']
    readonly_fields = ['unit_price']

    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'product']
    search_fields = ['sku', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
