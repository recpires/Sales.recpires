from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.utils import timezone
from .models import (
    Store, Product, ProductVariant, Category, Coupon,
    Order, OrderItem,
    Supplier, PurchaseOrder, PurchaseOrderItem # Novos modelos
)
from .serializers import (
    StoreSerializer, ProductSerializer, ProductVariantSerializer, CategorySerializer, CouponSerializer,
    OrderSerializer, OrderItemSerializer,
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer # Novos serializers
)
from .permissions import IsOwnerOrReadOnly

# Mixin para garantir que o objeto está relacionado à Store do usuário
class StoreOwnedMixin:
    def get_queryset(self):
        # Permite superusuário ver tudo, caso contrário, filtra pela loja do usuário
        if self.request.user.is_superuser:
            return super().get_queryset(self.request).all()
        try:
            store = self.request.user.store_profile
            return super().get_queryset(self.request).filter(store=store)
        except Store.DoesNotExist:
            return super().get_queryset(self.request).none()

    def perform_create(self, serializer):
        # Garante que o novo objeto está ligado à loja do usuário
        try:
            store = self.request.user.store_profile
            serializer.save(store=store)
        except Store.DoesNotExist:
            return Response({"detail": "Usuário não tem uma loja associada."}, status=status.HTTP_400_BAD_REQUEST)

# --- Existing Viewsets ---

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Store.objects.all()
        # Permite que um usuário veja a própria loja.
        return Store.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    # Adiciona ação para obter a loja do usuário logado
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_store(self, request):
        try:
            store = request.user.store_profile
            serializer = self.get_serializer(store)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response({"detail": "Nenhuma loja encontrada para este usuário."}, status=status.HTTP_404_NOT_FOUND)

class CategoryViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class ProductVariantViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class ProductViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class CouponViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    # Ação para aplicar cupom no checkout (validação)
    @action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        code = request.data.get('code')
        store_slug = request.data.get('store_slug') # Deve ser passado pelo frontend

        if not code or not store_slug:
            return Response({"detail": "Código e slug da loja são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(slug=store_slug)
        except Store.DoesNotExist:
            return Response({"detail": "Loja não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            coupon = Coupon.objects.get(
                store=store,
                code__iexact=code, 
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({"detail": "Cupom inválido ou expirado."}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    # Adicionando ação para marcar como pago
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def mark_as_paid(self, request, pk=None):
        order = self.get_object()
        if order.status == 'PENDING':
            order.status = 'PAID'
            order.paid_at = timezone.now()
            order.save()
            return Response({'status': 'Pedido marcado como pago'}, status=status.HTTP_200_OK)
        return Response({'status': 'Status atual não é pendente para ser pago.'}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------
#               NOVOS VIEWSETS PARA PO
# ----------------------------------------------------

class SupplierViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class PurchaseOrderViewSet(StoreOwnedMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    # Ação para receber itens de um PO e atualizar o estoque
    @action(detail=True, methods=['post'])
    def receive_items(self, request, pk=None):
        po = self.get_object()
        items_received_data = request.data.get('items', [])
        
        if po.status in ['RECEIVED_FULL', 'CANCELLED']:
            return Response({"detail": "O pedido já foi recebido totalmente ou cancelado."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not items_received_data:
            return Response({"detail": "Nenhum item recebido fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
        is_full_receipt = True
        
        for item_data in items_received_data:
            po_item_id = item_data.get('id')
            received_quantity = item_data.get('received_quantity', 0)
            
            if not po_item_id or received_quantity <= 0:
                continue

            try:
                po_item = po.po_items.get(id=po_item_id)
            except PurchaseOrderItem.DoesNotExist:
                return Response({"detail": f"Item do PO com ID {po_item_id} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
            # Garante que não recebemos mais do que o pedido menos o que já foi recebido
            available_to_receive = po_item.ordered_quantity - po_item.received_quantity
            
            if received_quantity > available_to_receive:
                return Response({"detail": f"Tentativa de receber {received_quantity} para o item {po_item_id}, mas só faltam {available_to_receive}."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Atualiza a quantidade recebida e o estoque (Entrada de estoque)
            po_item.received_quantity += received_quantity
            po_item.variant.stock_quantity += received_quantity # Entrada de Estoque!
            
            po_item.variant.save()
            po_item.save()
            
            if po_item.received_quantity < po_item.ordered_quantity:
                is_full_receipt = False
        
        # Atualiza o status do PO
        if is_full_receipt:
            po.status = 'RECEIVED_FULL'
        elif any(item.received_quantity > 0 for item in po.po_items.all()):
            po.status = 'RECEIVED_PARTIAL'
        else:
            po.status = 'ORDERED' # Se nada foi recebido, mantém como Ordered

        po.save()
        
        # Recarrega o PO com os dados atualizados para a resposta
        serializer = self.get_serializer(po)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Ação para obter itens de um PO
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        po = self.get_object()
        items = po.po_items.all()
        serializer = PurchaseOrderItemSerializer(items, many=True)
        return Response(serializer.data)