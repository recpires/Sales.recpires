from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from .models import Store, Product, ProductVariant, Order, OrderItem
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    OrderSerializer,
    OrderItemSerializer,
)

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

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
        try:
            store = user.store
            return Product.objects.filter(store=store).select_related('store').prefetch_related('variants')
        except Store.DoesNotExist:
            return Product.objects.none()

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