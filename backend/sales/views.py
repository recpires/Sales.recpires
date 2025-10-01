from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Order, OrderItem
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderItemSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.

    list: Get all products
    create: Create a new product
    retrieve: Get a specific product by ID
    update: Update a product
    partial_update: Partially update a product
    destroy: Delete a product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Optionally filter products by query parameters:
        - search: search in name and description
        - is_active: filter by active status
        - min_price, max_price: price range filtering
        """
        queryset = Product.objects.all()

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Price range filtering
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        """Add stock to a product"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Quantity must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.stock += quantity
            product.save()

            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders.

    list: Get all orders
    create: Create a new order with items
    retrieve: Get a specific order by ID
    update: Update an order
    partial_update: Partially update an order
    destroy: Delete an order
    """
    queryset = Order.objects.all()

    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Optionally filter orders by query parameters:
        - status: filter by order status
        - customer_email: filter by customer email
        """
        queryset = Order.objects.all()

        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by customer email
        customer_email = self.request.query_params.get('customer_email', None)
        if customer_email:
            queryset = queryset.filter(customer_email__icontains=customer_email)

        return queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def recalculate_total(self, request, pk=None):
        """Recalculate order total"""
        order = self.get_object()
        order.calculate_total()

        serializer = self.get_serializer(order)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for order items.

    list: Get all order items
    create: Create a new order item
    retrieve: Get a specific order item by ID
    update: Update an order item
    partial_update: Partially update an order item
    destroy: Delete an order item
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        """Optionally filter order items by order ID"""
        queryset = OrderItem.objects.all()

        order_id = self.request.query_params.get('order_id', None)
        if order_id:
            queryset = queryset.filter(order_id=order_id)

        return queryset

    def perform_create(self, serializer):
        """Auto-recalculate order total after creating an item"""
        order_item = serializer.save()
        order_item.order.calculate_total()

    def perform_update(self, serializer):
        """Auto-recalculate order total after updating an item"""
        order_item = serializer.save()
        order_item.order.calculate_total()

    def perform_destroy(self, instance):
        """Auto-recalculate order total after deleting an item"""
        order = instance.order
        instance.delete()
        order.calculate_total()