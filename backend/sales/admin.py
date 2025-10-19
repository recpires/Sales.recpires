from django.contrib import admin
from .models import Product, ProductVariant, Store, Order, OrderItem

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'color', 'size', 'price', 'stock', 'is_active', 'image')
    show_change_link = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'is_active', 'created_at')
    list_filter = ('store', 'is_active',)
    search_fields = ('name',)
    inlines = [ProductVariantInline]

admin.site.register(Store)
admin.site.register(ProductVariant)
admin.site.register(Order)
admin.site.register(OrderItem)
