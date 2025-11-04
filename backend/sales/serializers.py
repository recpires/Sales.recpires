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
    """
    Serializer principal para CRIAR e LER produtos.
    Ele agora aceita a criação de variantes aninhadas.
    """
    
    # Define o serializer de variantes aninhadas.
    # 'many=True' = é uma lista
    # 'required=False' = não é obrigatório (para produtos simples)
    variants = ProductVariantSerializer(many=True, required=False)
    
    # Campo de imagem para upload
    # 'required=False' = a imagem é opcional
    # 'write_only=True' = usado apenas para criar/atualizar, não mostra na leitura
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    
    # Campo de imagem para LEITURA (mostra a URL completa)
    image_url = serializers.SerializerMethodField(read_only=True)
    
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Product
        # --- CAMPOS CORRIGIDOS ---
        # Adicionamos 'sku', 'price', 'stock', 'category' (para produto simples)
        # Adicionamos 'variants' (para produto com variantes)
        # Adicionamos 'image' (para o upload) e 'image_url' (para leitura)
        fields = [
            'id', 'store', 'store_name', 'name', 'description', 'sku', 
            'price', 'stock', 'category', 'is_active', 
            'image', 'image_url', 'variants', 'created_at'
        ]
        read_only_fields = ['id', 'store', 'store_name', 'created_at']

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