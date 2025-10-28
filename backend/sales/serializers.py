from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate,
    Category, Review, Coupon, Wishlist
    # CORREÇÃO: Removido 'ProductCategory', que não existe mais.
)


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


# --- Serializers de Produto ---

class ProductVariantSerializer(serializers.ModelSerializer):
    """ Serializer para Variações (Cor, Tamanho, Estoque, Preço) """
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    
    # CORREÇÃO: 'image' agora é um SerializerMethodField para retornar a URL completa
    image = serializers.SerializerMethodField() 

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'color', 'color_display', 'size', 'size_display', 
            'model', 'stock', 'price', 'image', 'is_active'
        ]
        read_only_fields = ['id']
        
        # MELHORIA: Validação de estoque movida para o serializer
        extra_kwargs = {
            'stock': {'validators': []} # Remove validadores do model para tratar no .validate()
        }

    def get_image(self, obj):
        """ Retorna a URL absoluta da imagem da variante ou do produto principal """
        request = self.context.get('request')
        image_obj = obj.image or obj.product.image # Usa imagem da variante, ou a do produto
        
        if image_obj and request:
            return request.build_absolute_uri(image_obj.url)
        elif image_obj:
            return image_obj.url
        return None

    def validate_stock(self, value):
        """ Garante que o estoque não seja negativo ao ser definido """
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
        """ Pega recursivamente as sub-categorias ativas """
        if obj.children.exists():
            # Passa o 'context' (que inclui o 'request') para os filhos
            return CategorySerializer(
                obj.children.filter(is_active=True), 
                many=True, 
                context=self.context
            ).data
        return []

    def get_product_count(self, obj):
        """ CORREÇÃO: Conta produtos usando 'obj.products' (o ManyToMany) """
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """ Serializer para o Produto "Pai" (detalhes completos) """
    store_name = serializers.CharField(source='store.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    
    # Propriedades do Model
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    # CORREÇÃO: 'categories' agora é um SerializerMethodField
    categories = CategorySerializer(many=True, read_only=True) 
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # CORREÇÃO: Removidos campos que não existem em Product (price, stock, etc.)
        # CORREÇÃO: Unificadas as duas 'class Meta'
        fields = [
            'id', 'store', 'store_name', 'name', 'description', 'is_active', 'image',
            'categories', 'variants', 'total_stock', 
            'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store', 'created_at', 'updated_at']

    def get_image(self, obj):
        """ Retorna a URL absoluta da imagem principal do produto """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductLiteSerializer(serializers.ModelSerializer):
    """
    MELHORIA: Serializer "leve" para listas (ex: Wishlist, Carrinho), 
    evitando N+1 queries e recursão.
    """
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'image', 'price'] # 'slug' não existe no model, remover se for o caso

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
        
    def get_price(self, obj):
        """ Pega o preço da primeira variante (ou o menor preço) """
        first_variant = obj.variants.filter(is_active=True).first()
        if first_variant:
            return first_variant.price
        return None

# --- Serializers de Pedido ---

class OrderItemSerializer(serializers.ModelSerializer):
    """ Serializer para os Itens *dentro* de um pedido """
    
    # 'variant' será o ID (para escrita), 'variant_details' será o objeto (para leitura)
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    subtotal = serializers.DecimalField(source='get_subtotal', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_details', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal', 'unit_price'] # unit_price é snapshot

    # CORREÇÃO: Removido o 'validate'. 
    # A lógica de estoque já é tratada atomicamente pelo OrderItem.save() 
    # (que chamamos no OrderSerializer.create) e pelo model.
    # Duplicar a lógica aqui causa bugs.


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    # CORREÇÃO: Removida classe duplicada
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'status', 'note', 'is_automatic', 'created_at']
        read_only_fields = ['id', 'is_automatic', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """ Serializer para o Pedido (completo) """
    
    # CORREÇÃO: 'items' não é mais read_only para permitir criação
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
        # CORREÇÃO: Lógica de criação de itens aninhados
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            try:
                # O .save() do OrderItem (do models.py) vai cuidar do estoque
                OrderItem.objects.create(order=order, **item_data)
            except ValueError as e:
                # Se o .save() falhar (ex: estoque), cancela a criação do pedido
                order.delete()
                raise serializers.ValidationError(f"Erro ao adicionar item: {e}")

        order.calculate_total() # Calcula o total final
        order.set_status('pending', note='Pedido criado com sucesso.') # Seta o status inicial
        return order

    def update(self, instance, validated_data):
        # Lógica de atualização de Pedido (ex: mudar endereço, nome)
        # Nota: Itens são tratados separadamente (geralmente em endpoints /orders/ID/items/)
        validated_data.pop('items', None) # Remove 'items' para evitar atualização aninhada
        
        # Atualiza status APENAS pelo set_status
        new_status = validated_data.pop('status', None)
        
        instance = super().update(instance, validated_data)

        if new_status and instance.status != new_status:
             instance.set_status(new_status, note='Status atualizado via API', automatic=False)

        # CORREÇÃO: Removido 'return' duplicado e inacessível
        return instance


# --- Outros Serializers ---

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
        """ Associa o usuário logado automaticamente """
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
    # MELHORIA: Trocado ProductSerializer por ProductLiteSerializer
    # para evitar carregar todas as variantes em cada item da wishlist.
    product_details = ProductLiteSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        """ Associa o usuário logado automaticamente """
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError("Usuário não autenticado.")
        
        # Evita duplicatas
        try:
            return super().create(validated_data)
        except Exception: # IntegrityError (unique_together)
             raise serializers.ValidationError("Este item já está na sua lista de desejos.")