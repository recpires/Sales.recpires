from rest_framework import serializers
from .models import (
    Product, ProductVariant, Category, Store, Coupon, Order, OrderItem, 
    OrderStatusUpdate, Review, WishlistItem
)

# ... (Outros Serializers ProductVariantSerializer, OrderSerializer, etc. - mantidos iguais)
class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo ProductVariant.
    """
    class Meta:
        model = ProductVariant
        fields = (
            'id', 'product', 'price', 'stock', 'sku', 'color', 'size', 
            'is_master', 'created_at', 'updated_at'
        )
        read_only_fields = ('product', 'created_at', 'updated_at', 'is_master')


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Product, incluindo a criação aninhada da ProductVariant.
    """
    variants = ProductVariantSerializer(many=True, read_only=True)
    image = serializers.ImageField(max_length=None, use_url=True, required=False)

    # Campos Write-Only para a Variante Inicial (preços, estoque e sku agora pertencem à variante)
    initial_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, required=True
    )
    initial_stock = serializers.IntegerField(
        write_only=True, required=True, min_value=0
    )
    initial_sku = serializers.CharField(
        max_length=50, write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'store', 'is_active', 
            'created_at', 'updated_at', 'image', 'category', 'variants',
            # Inclui os campos write-only no fields da Meta
            'initial_price', 'initial_stock', 'initial_sku',
        )
        # Removemos price, sku e stock do read_only_fields pois não existem no modelo Product
        read_only_fields = ('created_at', 'updated_at', 'variants')

    def create(self, validated_data):
        # 1. Extrai os dados que pertencem à ProductVariant inicial
        initial_price = validated_data.pop('initial_price')
        initial_stock = validated_data.pop('initial_stock')
        # Use get com valor padrão para campos opcionais
        initial_sku = validated_data.pop('initial_sku', '')
        
        # 2. Cria o Produto (o DRF lida com o campo ImageField corretamente)
        product = Product.objects.create(**validated_data)

        # 3. Cria a Variante Mestra (Inicial) usando os dados extraídos
        ProductVariant.objects.create(
            product=product,
            price=initial_price,
            stock=initial_stock,
            sku=initial_sku,
            is_master=True
        )

        return product