from rest_framework import serializers
from .models import Store, Product, ProductVariant # <--- APENAS OS MODELS QUE PRECISAMOS
from django.db import transaction

class StoreSerializer(serializers.ModelSerializer):
    """ Serializer para a Loja (Sem alterações) """
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active']
        read_only_fields = ['id', 'owner']

# ---
# NOVO SERIALIZER PARA CRIAR VARIANTES
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

    def get_image_url(self, obj):
        """ Pega a URL da imagem principal do produto """
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None
        
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