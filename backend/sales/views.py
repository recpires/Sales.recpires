from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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

    def perform_create(self, serializer):
        """Define o owner e valida que o usuário ainda não tem loja."""
        print(f"[DEBUG] User: {self.request.user}, Data: {serializer.validated_data}")
        if Store.objects.filter(owner=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Você já possui uma loja cadastrada."})
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            print(f"[ERROR] {e}")
            raise

    def get_queryset(self):
        """Cada usuário vê apenas sua própria loja."""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('store').prefetch_related('variants')
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        """Opções de variação disponíveis (cores, tamanhos, modelos) para o produto."""
        product = self.get_object()
        qs = product.variants.filter(is_active=True)
        data = {
            'colors': list(qs.exclude(color__isnull=True).values_list('color', flat=True).distinct()),
            'sizes': list(qs.exclude(size__isnull=True).values_list('size', flat=True).distinct()),
            'models': list(qs.exclude(model__isnull=True).values_list('model', flat=True).distinct()),
        }
        return Response(data)


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista/filtra variantes por produto, cor, tamanho, modelo, disponibilidade e preço."""
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

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
    queryset = Order.objects.all().select_related('store').prefetch_related('items__product', 'items__variant', 'status_updates')
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """Atualiza o status do pedido e registra histórico."""
        order = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '')
        try:
            order.set_status(new_status, note=note, automatic=False)
            return Response({'status': order.status})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_cod_paid(self, request, pk=None):
        """Marca pagamento na entrega (COD) como pago."""
        order = self.get_object()
        try:
            order.mark_cod_paid()
            return Response({'payment_status': order.payment_status, 'paid_at': order.paid_at})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'product', 'variant').all()
    serializer_class = OrderItemSerializer