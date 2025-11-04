from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
# --- AQUI: IMPORTADO O MultiPartParser E FormParser ---
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q

from .models import (
    Store, Product, ProductVariant, Order, OrderItem,
    Category, Review, Coupon, Wishlist
)
from .serializers import (
    StoreSerializer,
    ProductSerializer,     # Deve ser o NOVO serializer que criamos
    ProductVariantSerializer, # Deve ser o NOVO serializer que criamos
    OrderSerializer,
    OrderItemSerializer,
    CategorySerializer,
    ReviewSerializer,
    CouponSerializer,
    WishlistSerializer,
)

class StoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet para a Loja do Vendedor. (Sem alterações)
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_store(self, request):
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
        if Store.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "Você já possui uma loja cadastrada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Produtos (o container principal).
    """
    # --- AQUI: Removido 'prefetch_related('categories')' pois 'category' é um CharField
    queryset = Product.objects.all().select_related('store').prefetch_related('variants')
    serializer_class = ProductSerializer # <--- DEVE SER O NOVO SERIALIZER
    
    # --- AQUI: Adicionado os Parsers para aceitar upload de imagem ---
    parser_classes = [MultiPartParser, FormParser]
    
    permission_classes = [IsAuthenticated] # Ajustado em get_permissions

    def get_permissions(self):
        """Permite que qualquer um (AllowAny) veja produtos (list, retrieve)."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # --- AQUI: REMOVIDA a ação @action 'options' inteira ---
    # A lógica dela dependia dos modelos Attribute/AttributeValue que foram removidos.
    # @action(detail=True, methods=['get'])
    # def options(self, request, pk=None):
    #     ... (código removido) ...

    def get_queryset(self):
        """
        Clientes veem todos os produtos ativos.
        Donos de loja veem todos os seus produtos (ativos ou não).
        """
        user = self.request.user
        
        # --- AQUI: Removido 'prefetch_related('categories')'
        base_qs = Product.objects.all().select_related('store').prefetch_related('variants')
        
        if user.is_staff:
            return base_qs

        if not user.is_authenticated or not hasattr(user, 'store'):
             return base_qs.filter(is_active=True)
        
        # Dono de loja vê seus próprios produtos
        return base_qs.filter(store=user.store)

    def perform_create(self, serializer):
        """Associa o produto à loja do usuário logado. (Está perfeito)"""
        try:
            store = self.request.user.store
        except Store.DoesNotExist:
            raise ValidationError({"detail": "Você precisa criar uma loja antes de adicionar produtos."})
        serializer.save(store=store)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Variantes (aninhado em /products/{product_pk}/variants/)
    """
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer # <--- DEVE SER O NOVO SERIALIZER
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filtra variantes baseado na URL aninhada (product_pk)
        """
        qs = super().get_queryset().filter(
            product_id=self.kwargs.get('product_pk')
        )
        
        user = self.request.user
        
        if not user.is_staff:
             qs = qs.filter(is_active=True)

        # --- AQUI: REMOVIDA toda a lógica de filtro por 'values' ---
        # A lógica antiga (p.get('color'), p.get('size')) estava quebrada
        # pois dependia dos modelos Attribute/AttributeValue.
        
        p = self.request.query_params
        if p.get('in_stock'):
            qs = qs.filter(stock__gt=0)
            
        return qs.order_by('id') # Alterado de 'price' para 'id'

    def perform_create(self, serializer):
        """Associa a variante ao produto pai da URL."""
        try:
            product = Product.objects.get(
                pk=self.kwargs.get('product_pk'),
                store=self.request.user.store # Garante que o dono da loja só adicione ao seu produto
            )
        except Product.DoesNotExist:
            raise ValidationError("Produto não encontrado ou não pertence à sua loja.")
        except Store.DoesNotExist:
            raise ValidationError("Você não possui uma loja.")
            
        serializer.save(product=product)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Pedidos (Sem alterações necessárias por enquanto)
    """
    queryset = Order.objects.all().select_related('store').prefetch_related('items__variant__product', 'status_updates')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        
        try:
            store = user.store
            return super().get_queryset().filter(store=store)
        except Store.DoesNotExist:
            return Order.objects.none()

    def perform_create(self, serializer):
        try:
            store = self.request.user.store
            serializer.save(store=store)
        except Store.DoesNotExist:
            serializer.save() 
    
    # ... (Restante do OrderViewSet sem alterações) ...
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
    """
    ViewSet para Itens de Pedido (Sem alterações necessárias)
    """
    queryset = OrderItem.objects.select_related('order', 'variant__product').all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_pk = self.kwargs.get('order_pk')
        user = self.request.user

        if user.is_staff:
            return super().get_queryset().filter(order_id=order_pk)
        
        try:
            store = user.store
            return super().get_queryset().filter(
                order_id=order_pk,
                order__store=store 
            )
        except Store.DoesNotExist:
            return OrderItem.objects.none()

    def perform_create(self, serializer):
        try:
            order = Order.objects.get(
                pk=self.kwargs.get('order_pk'),
                store=self.request.user.store
            )
        except Order.DoesNotExist:
            raise ValidationError("Pedido não encontrado ou não pertence à sua loja.")
        except Store.DoesNotExist:
            raise ValidationError("Você não possui uma loja.")
        
        serializer.save(order=order)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Categorias.
    """
    # --- AQUI: Assumindo que Category é um MODELO, não um CharField ---
    # Se 'category' for um CharField no seu models.py, este ViewSet
    # não será usado para criar produtos.
    queryset = Category.objects.filter(is_active=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] 
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'products']:
            return [AllowAny()]
        return [IsAuthenticated(),] # Idealmente: IsAdminUser

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Retorna todos os produtos ativos desta categoria."""
        category = self.get_object()
        
        # --- AQUI: A query foi alterada para 'category__iexact=category.name' ---
        # Isso assume que 'category' no Product é um CharField
        products = Product.objects.filter(
            category__iexact=category.name, # <--- MUDANÇA CRÍTICA
            is_active=True
        ).select_related('store').prefetch_related('variants')

        # Filtros de Preço
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if min_price:
            try:
                products = products.filter(variants__price__gte=Decimal(min_price))
            except Exception: pass
        if max_price:
            try:
                products = products.filter(variants__price__lte=Decimal(max_price))
            except Exception: pass

        serializer = ProductSerializer(products.distinct(), many=True, context={'request': request})
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Reviews (Sem alterações necessárias)
    """
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()] 

    def get_queryset(self):
        qs = super().get_queryset().filter(
            product_id=self.kwargs.get('product_pk')
        ).select_related('user', 'product')
        
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        try:
            product = Product.objects.get(pk=self.kwargs.get('product_pk'))
        except Product.DoesNotExist:
             raise ValidationError("Produto não encontrado.")

        # Lógica de verificação de compra está correta
        has_purchased = OrderItem.objects.filter(
            Q(order__customer_email=user.email) | Q(order__customer_name=user.username),
            variant__product=product,
            order__payment_status='paid'
        ).exists()

        try:
            serializer.save(user=user, product=product, is_verified_purchase=has_purchased)
        except IntegrityError:
            raise ValidationError({"detail": "Você já avaliou este produto."})


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Cupons (Sem alterações necessárias)
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated] # Idealmente: IsAdminUser

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Coupon.objects.all()
        return Coupon.objects.none() 

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_coupon(self, request):
        code = request.data.get('code')
        total = request.data.get('total', 0)

        if not code:
            return Response({'error': 'Código do cupom é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        if not total or Decimal(str(total)) <= 0:
             return Response({'error': 'Valor total é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response({'error': 'Cupom não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        is_valid, message = coupon.is_valid()
        if not is_valid:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        order_total = Decimal(str(total))
        if order_total < coupon.min_purchase_amount:
            return Response({
                'error': f'Valor mínimo de compra: R$ {coupon.min_purchase_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.calculate_discount(order_total)

        return Response({
            'valid': True,
            'coupon_code': coupon.code,
            'discount_amount': discount,
            'final_total': order_total - discount
        })


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet para a Lista de Desejos (Sem alterações necessárias)
    """
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
             raise ValidationError({"detail": "Este item já está na sua lista de desejos."})

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product') 

        if not product_id:
            return Response({'error': 'product é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

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
            'item': WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)