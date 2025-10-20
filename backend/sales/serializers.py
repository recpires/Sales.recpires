from rest_framework import serializers
from .models import Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'color', 'size', 'model', 'stock', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image(self, obj):
        """Return absolute URL for variant image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'store', 'name', 'description', 'price', 'color', 'size', 'stock',
            'sku', 'is_active', 'image', 'created_at', 'updated_at', 'variants'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusUpdate
        fields = ['status', 'note', 'is_automatic', 'created_at']
        read_only_fields = ['created_at', 'is_automatic']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'quantity', 'unit_price']
        read_only_fields = ['id']

    def validate(self, attrs):
        product = attrs.get('product') or getattr(self.instance, 'product', None)
        variant = attrs.get('variant') or getattr(self.instance, 'variant', None)
        if product and variant and variant.product_id != product.id:
            raise serializers.ValidationError("A variação selecionada não pertence ao produto informado.")
        # Se o produto tem variantes, a variante é obrigatória
        if product and not variant and product.variants.exists():
            raise serializers.ValidationError("Este produto possui variações. Selecione uma variação.")
        return attrs

    def create(self, validated_data):
        # Preenche unit_price com preço da variante ou do produto, se não enviado
        if not validated_data.get('unit_price'):
            variant = validated_data.get('variant')
            validated_data['unit_price'] = (variant.price if variant else validated_data['product'].price)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'unit_price' not in validated_data or not validated_data.get('unit_price'):
            variant = validated_data.get('variant', instance.variant)
            product = validated_data.get('product', instance.product)
            validated_data['unit_price'] = (variant.price if variant else product.price)
        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', 'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'status', 'payment_method', 'payment_status', 'paid_at',
            'total_amount', 'items', 'status_updates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'status_updates', 'paid_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        order.calculate_total()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # substitui itens do pedido (devolve estoque via delete e recria)
            instance.items.all().delete()
            for item in items_data:
                OrderItem.objects.create(order=instance, **item)
            instance.calculate_total()

        return instance


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']