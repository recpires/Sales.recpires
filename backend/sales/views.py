from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q

from .models import (
    Store, Product, ProductVariant, Order, OrderItem,
    Category, ProductCategory, Review, Coupon, Wishlist
)
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    OrderSerializer,
    OrderItemSerializer,
    CategorySerializer,
    ReviewSerializer,
    CouponSerializer,
    WishlistSerializer,
)

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_store(self, request):
        """Get the current user's store."""
        try:
            store = Store.objects.get(owner=request.user)
            serializer = self.get_serializer(store)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(
                {"detail": "Você ainda não possui uma loja cadastrada."},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """Override create para capturar erros de integridade."""
        if Store.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "Você já possui uma loja cadastrada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            return Response(
                {"detail": f"Erro de integridade: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Erro: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('store').prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        """Retorna opções de variação disponíveis (cores, tamanhos, modelos)."""
        product = self.get_object()
        qs = product.variants.filter(is_active=True)
        data = {
            'colors': list(qs.values_list('color', flat=True).distinct()),
            'sizes': list(qs.values_list('size', flat=True).distinct()),
            'models': list(qs.exclude(model='').values_list('model', flat=True).distinct()),
        }
        return Response(data)

    @action(detail=True, methods=['post'])
    def add_variant(self, request, pk=None):
        """Adiciona variação via método adicionar_variacao."""
        product = self.get_object()
        try:
            variant = product.adicionar_variacao(
                cor=request.data.get('color'),
                tamanho=request.data.get('size'),
                quantidade=request.data.get('stock', 0),
                preco=request.data.get('price'),
                modelo=request.data.get('model', ''),
                sku=request.data.get('sku')
            )
            serializer = ProductVariantSerializer(variant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Product.objects.all().select_related('store').prefetch_related('variants')
        # Regular users can see all products (customer view)
        if not hasattr(user, 'store'):
            return Product.objects.all().select_related('store').prefetch_related('variants')
        # Store owners see only their products
        return Product.objects.filter(store=user.store).select_related('store').prefetch_related('variants')

    def perform_create(self, serializer):
        try:
            store = self.request.user.store
        except Store.DoesNotExist:
            raise ValidationError({"store": ["Você precisa criar uma loja antes de adicionar produtos."]})
        serializer.save(store=store)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

        # Filtrar por loja do usuário (não-admin)
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            try:
                store = user.store
                qs = qs.filter(product__store=store)
            except Store.DoesNotExist:
                return ProductVariant.objects.none()

        if p.get('product'):
            qs = qs.filter(product_id=p.get('product'))
        if p.get('color'):
            qs = qs.filter(color=p.get('color'))
        if p.get('size'):
            qs = qs.filter(size=p.get('size'))
        if p.get('model'):
            qs = qs.filter(model__iexact=p.get('model'))
        if p.get('sku'):
            qs = qs.filter(sku__icontains=p.get('sku'))

        val = (p.get('is_active') or '').lower()
        if val in ('1', 'true', 't', 'yes', 'y'):
            qs = qs.filter(is_active=True)
        elif val in ('0', 'false', 'f', 'no', 'n'):
            qs = qs.filter(is_active=False)

        val = (p.get('in_stock') or '').lower()
        if val in ('1', 'true', 't', 'yes', 'y'):
            qs = qs.filter(stock__gt=0)
        elif val in ('0', 'false', 'f', 'no', 'n'):
            qs = qs.filter(stock__lte=0)

        if p.get('min_price'):
            try:
                qs = qs.filter(price__gte=Decimal(p.get('min_price')))
            except Exception:
                pass
        if p.get('max_price'):
            try:
                qs = qs.filter(price__lte=Decimal(p.get('max_price')))
            except Exception:
                pass

        return qs.order_by('-created_at')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('store').prefetch_related('items__variant__product', 'status_updates')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all().select_related('store').prefetch_related('items__variant__product', 'status_updates')
        try:
            store = user.store
            return Order.objects.filter(store=store).select_related('store').prefetch_related('items__variant__product', 'status_updates')
        except Store.DoesNotExist:
            return Order.objects.none()

    def perform_create(self, serializer):
        try:
            store = self.request.user.store
        except Store.DoesNotExist:
            raise ValidationError({"store": ["Você precisa criar uma loja antes de criar pedidos."]})
        serializer.save(store=store)

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '')
        try:
            order.set_status(new_status, note=note, automatic=False)
            return Response({'status': order.status, 'status_display': order.get_status_display()})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_cod_paid(self, request, pk=None):
        order = self.get_object()
        try:
            order.mark_cod_paid()
            return Response({'payment_status': order.payment_status, 'paid_at': order.paid_at})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'variant__product').all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return OrderItem.objects.select_related('order', 'variant__product').all()
        try:
            store = user.store
            return OrderItem.objects.filter(order__store=store).select_related('order', 'variant__product')
        except Store.DoesNotExist:
            return OrderItem.objects.none()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_permissions(self):
        """Allow anyone to view categories, but only authenticated users can create/update/delete"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(
            product_categories__category=category,
            is_active=True
        ).select_related('store').prefetch_related('variants')

        # Apply filters
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow anyone to view reviews, but only authenticated users can create"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter reviews by product if specified"""
        qs = Review.objects.filter(is_approved=True).select_related('user', 'product')
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        """Set user automatically and check if user purchased the product"""
        product = serializer.validated_data.get('product')
        user = self.request.user

        # Check if user has purchased this product
        has_purchased = OrderItem.objects.filter(
            order__customer_email=user.email,
            product=product,
            order__payment_status='paid'
        ).exists()

        serializer.save(user=user, is_verified_purchase=has_purchased)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Admin sees all, regular users only see active coupons"""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)

    @action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        """Validate a coupon code for a specific order total"""
        code = request.data.get('code')
        total = request.data.get('total', 0)

        if not code:
            return Response({'error': 'Código do cupom é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            return Response({'error': 'Cupom não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        is_valid, message = coupon.is_valid()
        if not is_valid:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        if total < coupon.min_purchase_amount:
            return Response({
                'error': f'Valor mínimo de compra: R$ {coupon.min_purchase_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.calculate_discount(Decimal(str(total)))

        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount': float(discount),
            'final_total': float(Decimal(str(total)) - discount)
        })


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users only see their own wishlist"""
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        """Set user automatically"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle product in wishlist (add if not exists, remove if exists)"""
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'product_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            wishlist_item.delete()
            return Response({'action': 'removed', 'message': 'Produto removido dos favoritos'})

        return Response({
            'action': 'added',
            'message': 'Produto adicionado aos favoritos',
            'wishlist': WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)