from rest_framework import serializers
from .models import (
    Store, Product, ProductVariant, Category, Attribute, AttributeValue,
    Order, OrderItem, OrderStatusUpdate, Review, Coupon, Wishlist
)
from django.db import transaction


# --- BASIC SERIALIZERS ---

class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for attribute values"""
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']
        read_only_fields = ['id']


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer for attributes"""
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'values']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'is_active']
        read_only_fields = ['id', 'slug']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for stores"""
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active']
        read_only_fields = ['id', 'owner']


# ---
# PRODUCT VARIANT SERIALIZER
# ---
class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer para as Variantes.
    Usado para ler E escrever as variantes dentro do Produto.
    """
    class Meta:
        model = ProductVariant
        fields = [
            'id', 
            'name',  # <--- O campo "Nome da Variante" (ex: "Tamanho M")
            'sku', 
            'price', 
            'stock'
        ]
        read_only_fields = ['id']


# ---
# SERIALIZER DE PRODUTO PRINCIPAL (TOTALMENTE CORRIGIDO)
# ---
class ProductSerializer(serializers.ModelSerializer):
    """ Serializer para o Produto "Pai" (detalhes completos) """
    store_name = serializers.SerializerMethodField()
    # <--- OK: 'variants' agora usa o ProductVariantSerializer atualizado
    variants = ProductVariantSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    categories = CategorySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    # <--- ALTERADO: Adicionado 'variant_attributes'
    variant_attributes = AttributeSerializer(many=True, read_only=True)

    def get_store_name(self, obj):
        """Retorna o nome da loja ou None se não houver loja"""
        return obj.store.name if obj.store else None

    # <--- ADDED: Accept price/stock for simple products (write-only)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, required=False,
        help_text="Price for simple products (creates default variant)"
    )
    stock = serializers.IntegerField(
        write_only=True, required=False,
        help_text="Stock for simple products (creates default variant)"
    )
    sku = serializers.CharField(
        write_only=True, required=False,
        help_text="SKU for simple products (creates default variant)"
    )

    class Meta:
        model = Product
        # <--- ALTERADO: Adicionado 'variant_attributes', 'price', 'stock', 'sku'
        fields = [
            'id', 'store', 'store_name', 'name', 'description', 'is_active', 'image',
            'categories', 'variant_attributes', 'variants', 'total_stock',
            'average_rating', 'review_count', 'created_at', 'updated_at',
            'price', 'stock', 'sku'  # Added for simple product creation
        ]
        read_only_fields = ['id', 'store', 'created_at', 'updated_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def create(self, validated_data):
        """
        Create product and optionally a default variant if price/stock provided.
        Handles both simple products and products with explicit variants.

        Note: The 'store' field is passed via perform_create in the ViewSet.
        """
        # Extract price/stock/sku if provided (for simple products)
        price = validated_data.pop('price', None)
        stock = validated_data.pop('stock', None)
        sku = validated_data.pop('sku', None)

        # Create the product (store is passed from perform_create)
        product = Product.objects.create(**validated_data)

        # If price is provided, create a default variant
        if price is not None:
            # Generate SKU if not provided
            if not sku:
                sku = f"{product.name[:3].upper()}-{product.id}-DEFAULT"

            # Create default variant
            ProductVariant.objects.create(
                product=product,
                sku=sku,
                price=price,
                stock=stock if stock is not None else 0,
                is_active=True
            )

        return product


class ProductLiteSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Product, incluindo a criação aninhada da ProductVariant.
    """
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    # <--- ATENÇÃO: 'slug' não existe no seu model Product. 
    # Mantenha ou remova conforme seu model.
    class Meta:
        model = Product 
        fields = ['id', 'name', 'image', 'price'] 

    def get_image(self, obj):
        """ Pega a URL da imagem principal do produto """
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

    def get_price(self, obj):
        """Retorna o preço do produto (da primeira variante ou do preço principal)"""
        # Se produto tem variantes, pega o menor preço
        if obj.variants.exists():
            variant = obj.variants.filter(is_active=True).order_by('price').first()
            return variant.price if variant else None
        # Se não tem variantes, retorna o preço principal
        return obj.price
        
    def validate(self, data):
        """
        Validação customizada:
        - Se 'variants' existir, 'price' e 'stock' principais devem ser nulos.
        - Se 'variants' não existir, 'price' e 'stock' principais são obrigatórios.
        """
        has_variants = 'variants' in data and data['variants']
        
        if has_variants:
            # Produto com variantes: limpa preço/estoque principal
            data['price'] = None
            data['stock'] = None
        else:
            # Produto simples: valida preço/estoque principal
            if 'price' not in data or data['price'] is None:
                raise serializers.ValidationError({"price": "Preço é obrigatório para produtos simples."})
            if 'stock' not in data or data['stock'] is None:
                raise serializers.ValidationError({"stock": "Estoque é obrigatório para produtos simples."})
                
        return data

    @transaction.atomic  # Garante que tudo seja salvo junto (ou nada)
    def create(self, validated_data):
        """
        Sobrescreve o método 'create' para lidar com variantes.
        """
        # 1. Remove os dados das variantes (se existirem)
        variants_data = validated_data.pop('variants', [])

        # 2. Cria o objeto 'Product' principal
        product = Product.objects.create(**validated_data)

        # 3. Se houver dados de variantes, cria cada uma
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)

        return product


# --- ORDER SERIALIZERS ---

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for order status updates"""
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'order', 'status', 'note', 'is_automatic', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'variant', 'variant_name',
                 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'store', 'store_name', 'customer_name', 'customer_email',
                 'customer_phone', 'shipping_address', 'status', 'total_amount',
                 'payment_method', 'payment_status', 'paid_at', 'created_at',
                 'updated_at', 'items', 'status_updates']
        read_only_fields = ['id', 'total_amount', 'paid_at', 'created_at', 'updated_at']


# --- REVIEW SERIALIZERS ---

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name', 'rating',
                 'comment', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


# --- COUPON SERIALIZERS ---

class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons"""
    is_valid_now = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'min_purchase_amount',
                 'max_discount_amount', 'usage_limit', 'usage_count', 'valid_from',
                 'valid_until', 'is_active', 'is_valid_now', 'created_at', 'updated_at']
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']

    def get_is_valid_now(self, obj):
        return obj.is_valid()


# --- WISHLIST SERIALIZERS ---

class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist"""
    product_details = ProductLiteSerializer(source='product', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'user_name', 'product', 'product_details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
