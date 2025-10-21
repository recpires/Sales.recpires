from rest_framework import serializers
from .models import Store, Product, ProductVariant, Order, OrderItem, OrderStatusUpdate


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'phone', 'email', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'color', 'color_display', 'size', 'model',
            'stock', 'price', 'image', 'is_active', 'created_at', 'updated_at'
        ]
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
    total_stock = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'store', 'name', 'description', 'is_active', 'image',
            'created_at', 'updated_at', 'variants', 'total_stock'
        ]
        read_only_fields = ['id', 'store', 'created_at', 'updated_at', 'total_stock']


class OrderItemSerializer(serializers.ModelSerializer):
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    subtotal = serializers.DecimalField(source='get_subtotal', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'variant', 'variant_details', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'order', 'subtotal']

    def validate(self, attrs):
        variant = attrs.get('variant')
        quantity = attrs.get('quantity', 1)
        
        # Verifica estoque disponível
        if self.instance:
            # Editando item existente
            previous_qty = self.instance.quantity
            delta = quantity - previous_qty
            if delta > 0 and delta > variant.stock:
                raise serializers.ValidationError(
                    f"Estoque insuficiente. Disponível: {variant.stock}"
                )
        else:
            # Novo item
            if quantity > variant.stock:
                raise serializers.ValidationError(
                    f"Estoque insuficiente. Disponível: {variant.stock}"
                )
        
        return attrs


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'order', 'status', 'note', 'is_automatic', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'store', 'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'status', 'status_display', 'payment_method',
            'payment_status', 'paid_at', 'total_amount', 'items', 'status_updates',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store', 'total_amount', 'paid_at', 'created_at', 'updated_at']

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