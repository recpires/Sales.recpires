from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Store, Product, ProductVariant, Order, OrderItem
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    OrderSerializer,
    OrderItemSerializer,
)

# Se já existir, ignore esta classe
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

# Se já existir, ignore esta classe
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'product', 'variant').all()
    serializer_class = OrderItemSerializer

# Endpoint de variantes com filtros
class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
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

# Opcional: ação para listar opções de variação num produto
# Se seu ProductViewSet já existir, apenas adicione este método dentro da classe:
#   @action(detail=True, methods=['get'])
#   def options(self, request, pk=None):
#       product = self.get_object()
#       qs = product.variants.filter(is_active=True)
#       data = {
#           'colors': list(qs.exclude(color__isnull=True).values_list('color', flat=True).distinct()),
#           'sizes': list(qs.exclude(size__isnull=True).values_list('size', flat=True).distinct()),
#           'models': list(qs.exclude(model__isnull=True).values_list('model', flat=True).distinct()),
#       }
#       return Response(data)