from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate,
    Category, Review, Coupon, Wishlist,
    Attribute, AttributeValue  # <--- ALTERADO: Importa os novos models
)


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


# --- NOVOS SERIALIZERS para Atributos ---

class AttributeSerializer(serializers.ModelSerializer):
    """ Serializer para Atributos (ex: Cor, Tamanho) """
    class Meta:
        model = Attribute
        fields = ['id', 'name']


class AttributeValueSerializer(serializers.ModelSerializer):
    """ Serializer para Valores de Atributos (ex: Vermelho, M) """
    # <--- ALTERADO: Exibe o nome do atributo (ex: "Cor") em vez do ID
    attribute = serializers.StringRelatedField() 

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'value']


# --- Serializers de Produto (ALTERADOS) ---

class ProductVariantSerializer(serializers.ModelSerializer):
    """ Serializer para Variações (Flexível) """
    
    # <--- REMOVIDO: 'color_display' e 'size_display' não existem mais
    # color_display = ...
    # size_display = ...
    
    # <--- ALTERADO: Adicionado 'values' aninhado
    values = AttributeValueSerializer(many=True, read_only=True)
    
    image = serializers.SerializerMethodField() 

    class Meta:
        model = ProductVariant
        # <--- ALTERADO: Removidos 'color', 'color_display', 'size', 'size_display', 'model'
        # Adicionado 'values'
        fields = [
            'id', 'product', 'sku', 'values', 'stock', 'price', 'image', 'is_active'
        ]
        read_only_fields = ['id']
        
        extra_kwargs = {
            'stock': {'validators': []}
        }

    def get_image(self, obj):
        """ Retorna a URL absoluta da imagem da variante ou do produto principal """
        request = self.context.get('request')
        image_obj = obj.image or obj.product.image 
        
        if image_obj and request:
            return request.build_absolute_uri(image_obj.url)
        elif image_obj:
            return image_obj.url
        return None

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("O estoque não pode ser negativo.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    """ Serializer para Categorias """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'is_active', 'children', 'product_count']
        read_only_fields = ['id']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(
                obj.children.filter(is_active=True), 
                many=True, 
                context=self.context
            ).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """ Serializer para o Produto "Pai" (detalhes completos) """
    store_name = serializers.CharField(source='store.name', read_only=True)
    # <--- OK: 'variants' agora usa o ProductVariantSerializer atualizado
    variants = ProductVariantSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    categories = CategorySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    # <--- ALTERADO: Adicionado 'variant_attributes'
    variant_attributes = AttributeSerializer(many=True, read_only=True)

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
        """
        # Extract price/stock/sku if provided (for simple products)
        price = validated_data.pop('price', None)
        stock = validated_data.pop('stock', None)
        sku = validated_data.pop('sku', None)

        # Create the product
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
    Serializer "leve" para listas (Sem alterações necessárias)
    """
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    # <--- ATENÇÃO: 'slug' não existe no seu model Product. 
    # Mantenha ou remova conforme seu model.
    class Meta:
        model = Product 
        fields = ['id', 'name', 'image', 'price'] 

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
        
    def get_price(self, obj):
        """ Pega o preço da primeira variante (ou o menor preço) """
        # <--- OK: Esta lógica ainda funciona
        first_variant = obj.variants.filter(is_active=True).first()
        if first_variant:
            return first_variant.price
        return None

# --- Serializers de Pedido (Sem alterações necessárias) ---
# A lógica de 'OrderItem' aponta para 'ProductVariant', 
# então ela é independente das mudanças internas do ProductVariant.

class OrderItemSerializer(serializers.ModelSerializer):
    """ Serializer para os Itens *dentro* de um pedido """
    
    # <--- OK: 'variant_details' usará o ProductVariantSerializer atualizado
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    subtotal = serializers.DecimalField(source='get_subtotal', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_details', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal', 'unit_price'] 


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'status', 'note', 'is_automatic', 'created_at']
        read_only_fields = ['id', 'is_automatic', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """ Serializer para o Pedido (completo) """
    
    items = OrderItemSerializer(many=True) 
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'store', 'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'status', 'status_display', 'payment_method',
            'payment_status', 'paid_at', 'total_amount', 'items', 'status_updates',
            'coupon', 'discount_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'store', 'total_amount', 'paid_at', 
            'created_at', 'updated_at', 'status_updates', 'discount_amount'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            try:
                OrderItem.objects.create(order=order, **item_data)
            except ValueError as e:
                order.delete()
                raise serializers.ValidationError(f"Erro ao adicionar item: {e}")

        order.calculate_total() 
        order.set_status('pending', note='Pedido criado com sucesso.')
        return order

    def update(self, instance, validated_data):
        validated_data.pop('items', None)
        
        new_status = validated_data.pop('status', None)
        
        instance = super().update(instance, validated_data)

        if new_status and instance.status != new_status:
             instance.set_status(new_status, note='Status atualizado via API', automatic=False)

        return instance


# --- Outros Serializers (Sem alterações necessárias) ---

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'user_name', 'user_first_name', 'rating', 
            'title', 'comment', 'is_verified_purchase', 'is_approved', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_first_name', 
            'is_verified_purchase', 'is_approved', 'created_at'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CouponSerializer(serializers.ModelSerializer):
    is_valid_now = serializers.SerializerMethodField()
    valid_message = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_purchase_amount', 'max_discount_amount', 'usage_limit', 'usage_count',
            'valid_from', 'valid_until', 'is_active', 'is_valid_now', 'valid_message'
        ]
        read_only_fields = ['id', 'usage_count']

    def get_is_valid_now(self, obj):
        is_valid, _ = obj.is_valid()
        return is_valid

    def get_valid_message(self, obj):
        _, message = obj.is_valid()
        return message


class WishlistSerializer(serializers.ModelSerializer):
    # <--- OK: 'product_details' usa o ProductLiteSerializer, que ainda é válido.
    product_details = ProductLiteSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError("Usuário não autenticado.")
        
        try:
            return super().create(validated_data)
        except Exception: # IntegrityError (unique_together)
             raise serializers.ValidationError("Este item já está na sua lista de desejos.")