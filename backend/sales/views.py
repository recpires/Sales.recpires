from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Product, Order, OrderItem, Store
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    StoreSerializer
)


class StoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stores.

    list: Get all stores (or just user's store if admin)
    create: Create a new store (automatically linked to current user)
    retrieve: Get a specific store by ID
    update: Update a store
    partial_update: Partially update a store
    destroy: Delete a store
    my_store: Get or create current user's store
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Staff users can see all stores.
        Regular users can only see their own store.
        """
        if self.request.user.is_staff:
            return Store.objects.all()

        # Return user's store if they have one
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the owner to the current user"""
        from rest_framework.exceptions import ValidationError

        # Check if user already has a store
        if hasattr(self.request.user, 'store'):
            raise ValidationError('You already have a store')

        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_store(self, request):
        """Get the current user's store"""
        try:
            store = request.user.store
            serializer = self.get_serializer(store)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(
                {'error': 'You do not have a store yet. Please create one.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.

    list: Get all products (users see all, admins see only their products)
    create: Create a new product (automatically linked to admin's store)
    retrieve: Get a specific product by ID
    update: Update a product
    partial_update: Partially update a product
    destroy: Delete a product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Regular users see all products from all stores.
        Staff users (admins/sellers) only see products from their own store.

        Optionally filter products by query parameters:
        - search: search in name and description
        - is_active: filter by active status
        - min_price, max_price: price range filtering
        - store: filter by store ID
        """
        # Base queryset depends on user type
        if self.request.user.is_staff:
            # Admins only see their store's products
            try:
                store = self.request.user.store
                queryset = Product.objects.filter(store=store)
            except Store.DoesNotExist:
                # Admin doesn't have a store yet
                queryset = Product.objects.none()
        else:
            # Regular users see all products
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

        # Filter by store (for regular users to filter by specific store)
        store_id = self.request.query_params.get('store', None)
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        return queryset

    def perform_create(self, serializer):
        """Automatically set the store to the current user's store"""
        from rest_framework.exceptions import ValidationError, PermissionDenied

        if not self.request.user.is_staff:
            raise PermissionDenied('Only store owners can create products')

        try:
            store = self.request.user.store
            serializer.save(store=store)
        except Store.DoesNotExist:
            raise ValidationError('You must create a store before adding products')

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

    list: Get all orders (admins see only their store's orders)
    create: Create a new order with items
    retrieve: Get a specific order by ID
    update: Update an order
    partial_update: Partially update an order
    destroy: Delete an order
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Staff users only see orders from their store.
        Regular users see all orders.

        Optionally filter orders by query parameters:
        - status: filter by order status
        - customer_email: filter by customer email
        - store: filter by store ID
        """
        # Base queryset depends on user type
        if self.request.user.is_staff:
            # Admins only see their store's orders
            try:
                store = self.request.user.store
                queryset = Order.objects.filter(store=store)
            except Store.DoesNotExist:
                queryset = Order.objects.none()
        else:
            # Regular users see all orders
            queryset = Order.objects.all()

        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by customer email
        customer_email = self.request.query_params.get('customer_email', None)
        if customer_email:
            queryset = queryset.filter(customer_email__icontains=customer_email)

        # Filter by store (for regular users)
        store_id = self.request.query_params.get('store', None)
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """Wrap creation to return structured 400 responses when validation fails (e.g., insufficient stock)."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            out_serializer = OrderSerializer(order)
            return Response(out_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            # Prefer DRF ValidationError to return structured errors
            from rest_framework.exceptions import ValidationError as DRFValidationError
            if isinstance(exc, DRFValidationError):
                return Response({'errors': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
            # Fallback: return generic message
            return Response({'errors': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

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