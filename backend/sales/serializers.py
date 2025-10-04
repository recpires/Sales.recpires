from rest_framework import serializers
from .models import Product, Order, OrderItem, Store


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'email',
            'address', 'is_active', 'owner', 'owner_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    seller_name = serializers.CharField(source='store.owner.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'store', 'store_name', 'seller_name', 'name', 'description',
            'price', 'color', 'color_display', 'size', 'size_display', 'stock',
            'sku', 'is_active', 'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'store_name', 'seller_name']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_subtotal'
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit_price', 'subtotal'
        ]
        read_only_fields = ['unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', 'store_name', 'customer_name', 'customer_email',
            'customer_phone', 'shipping_address', 'status', 'total_amount',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount', 'store_name']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders with items"""
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'status', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.calculate_total()
        return order