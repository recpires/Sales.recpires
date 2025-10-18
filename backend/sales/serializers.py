from rest_framework import serializers
from .models import Product, Order, OrderItem, Store, ProductVariant
from django.db import transaction
from rest_framework.exceptions import ValidationError


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


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'color', 'size', 'stock', 'image', 'is_active']

    def get_image(self, obj):
        """Return absolute URL for variant image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    seller_name = serializers.CharField(source='store.owner.username', read_only=True)

    variants = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'store', 'store_name', 'seller_name', 'name', 'description',
            'price', 'color', 'color_display', 'size', 'size_display', 'stock',
            'sku', 'is_active', 'image', 'created_at', 'updated_at', 'variants'
        ]
        read_only_fields = ['store', 'created_at', 'updated_at', 'store_name', 'seller_name']

    def get_image(self, obj):
        """Return absolute URL for product image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_variants(self, obj):
        return ProductVariantSerializer(obj.variants.all(), many=True, context=self.context).data


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_subtotal'
    )
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all(), allow_null=True, required=False)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'quantity',
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

        # Create order and items inside a transaction to safely update stock
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item_data in items_data:
                variant = item_data.get('variant', None)
                product = item_data.get('product')
                quantity = item_data.get('quantity')

                # Resolve variant if provided as PK or object
                if variant:
                    if isinstance(variant, int):
                        try:
                            variant_obj = ProductVariant.objects.select_for_update().get(pk=variant)
                        except ProductVariant.DoesNotExist:
                            raise ValidationError(f"Variant with id {variant} does not exist")
                    else:
                        try:
                            variant_obj = ProductVariant.objects.select_for_update().get(pk=variant.id)
                        except ProductVariant.DoesNotExist:
                            raise ValidationError(f"Variant with id {variant.id} does not exist")

                    if variant_obj.stock < quantity:
                        raise ValidationError({
                            'stock': f"Insufficient stock for variant {variant_obj.sku}",
                            'available': variant_obj.stock,
                            'requested': quantity,
                        })

                    # decrement stock
                    variant_obj.stock -= quantity
                    variant_obj.save()

                    unit_price = variant_obj.price
                    OrderItem.objects.create(order=order, product=product, variant=variant_obj, quantity=quantity, unit_price=unit_price)
                else:
                    # no variant: operate on product stock
                    try:
                        product_obj = Product.objects.select_for_update().get(pk=product.id)
                    except Product.DoesNotExist:
                        raise ValidationError(f"Product with id {product.id} does not exist")

                    if product_obj.stock < quantity:
                        raise ValidationError({
                            'stock': f"Insufficient stock for product {product_obj.name}",
                            'available': product_obj.stock,
                            'requested': quantity,
                        })

                    product_obj.stock -= quantity
                    product_obj.save()

                    unit_price = product_obj.price
                    OrderItem.objects.create(order=order, product=product_obj, quantity=quantity, unit_price=unit_price)

            order.calculate_total()
            return order