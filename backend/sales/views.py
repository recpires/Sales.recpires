
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
    Category, Review, Coupon, Wishlist 
    # CORREÇÃO 1: Removido 'ProductCategory', que não existe mais.
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
    """
    ViewSet para a Loja do Vendedor.
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_store(self, request):
        """Retorna a loja do usuário logado."""
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
        """Impede que um usuário crie mais de uma loja."""
        if Store.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "Você já possui uma loja cadastrada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Admin vê tudo, usuários veem apenas sua própria loja."""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Produtos (o container principal).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated] # Ajustado em get_permissions

    def get_permissions(self):
        """Permite que qualquer um (AllowAny) veja produtos (list, retrieve)."""
        if self.action in ['list', 'retrieve', 'options']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        """Retorna opções de variação disponíveis (cores, tamanhos, modelos)."""
        product = self.get_object()
        qs = product.variants.filter(is_active=True, stock__gt=0)
        data = {
            'colors': list(qs.values_list('color', flat=True).distinct()),
            'sizes': list(qs.values_list('size', flat=True).distinct()),
            'models': list(qs.exclude(model='').values_list('model', flat=True).distinct()),
        }
        return Response(data)

    def get_queryset(self):
        """
        Clientes veem todos os produtos ativos.
        Donos de loja veem todos os seus produtos (ativos ou não).
        """
        user = self.request.user
        print('user:', user)
        if user.is_staff:
            print('TO AQUI 1')
            return Product.objects.all()

        # Se o usuário não está autenticado ou é um cliente (não dono de loja)
        if not user.is_authenticated or not hasattr(user, 'store'):
             print('TO AQUI 2')
             return Product.objects.filter(is_active=True)
        print('TO AQUI 3')
        # Dono de loja vê seus próprios produtos
        return Product.objects.filter(store=user.store)
    
    def perform_create(self, serializer):
        """Associa o produto à loja do usuário logado."""
        user = self.request.user
        print(f"DEBUG: User creating product: {user.username}")
        print(f"DEBUG: User has 'store' attribute: {hasattr(user, 'store')}")

        try:
            store = Store.objects.get(owner=user)
            print(f"DEBUG: Store found: {store.name} (ID: {store.id})")
        except Store.DoesNotExist:
            print(f"DEBUG: No store found for user {user.username}")
            raise ValidationError({"detail": "Você precisa criar uma loja antes de adicionar produtos."})

        print(f"DEBUG: Saving product with store: {store}")
        serializer.save(store=store)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Variantes (aninhado em /products/{product_pk}/variants/)
    """
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Permite que qualquer um (AllowAny) veja variantes."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        CORREÇÃO 2: Filtra variantes baseado na URL aninhada (product_pk)
        e também permite filtros adicionais por query params.
        """
        # Filtra pelo 'product_pk' da URL
        qs = super().get_queryset().filter(
            product_id=self.kwargs.get('product_pk')
        )
        
        user = self.request.user
        
        # Se o usuário não for staff, filtra apenas variantes ativas
        if not user.is_staff:
             qs = qs.filter(is_active=True)

        # Filtros adicionais da query string (ex: ?color=blue&size=M)
        p = self.request.query_params
        if p.get('color'):
            qs = qs.filter(color=p.get('color'))
        if p.get('size'):
            qs = qs.filter(size=p.get('size'))
        if p.get('model'):
            qs = qs.filter(model__iexact=p.get('model'))
        if p.get('in_stock'):
            qs = qs.filter(stock__gt=0)
            
        return qs.order_by('price')

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
    ViewSet para Pedidos (apenas para donos de loja).
    """
    queryset = Order.objects.all().select_related('store').prefetch_related('items__variant__product', 'status_updates')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] # Assumindo que clientes não veem /orders/

    def get_queryset(self):
        """Dono da loja vê apenas seus pedidos; Staff vê tudo."""
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        
        try:
            store = user.store
            return super().get_queryset().filter(store=store)
        except Store.DoesNotExist:
            return Order.objects.none()

    def perform_create(self, serializer):
        """
        Define a loja do pedido baseado no primeiro item
        ou na loja do usuário (se for dono).
        """
        # Lógica para criação de pedido (ex: checkout de cliente)
        # Esta lógica deve ser mais robusta, ex: pegar a loja do primeiro item.
        # Por enquanto, mantemos a lógica de "dono da loja cria pedido"
        try:
            store = self.request.user.store
            serializer.save(store=store)
        except Store.DoesNotExist:
            # Se for um cliente, a lógica de 'store' deve vir do Serializer
            # ou ser extraída dos itens.
            serializer.save() 
            # Nota: O OrderSerializer.create() precisa ser robusto

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """Muda o status de um pedido."""
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
        """Marca um pedido COD (Pagamento na Entrega) como pago."""
        order = self.get_object()
        try:
            order.mark_cod_paid()
            return Response({'payment_status': order.payment_status, 'paid_at': order.paid_at})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Itens de Pedido (aninhado em /orders/{order_pk}/items/)
    """
    queryset = OrderItem.objects.select_related('order', 'variant__product').all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        CORREÇÃO 2: Filtra itens baseado na URL aninhada (order_pk)
        e garante que o usuário seja dono da loja.
        """
        order_pk = self.kwargs.get('order_pk')
        user = self.request.user

        if user.is_staff:
            return super().get_queryset().filter(order_id=order_pk)
        
        try:
            store = user.store
            return super().get_queryset().filter(
                order_id=order_pk,
                order__store=store # Segurança: Garante que o item é de um pedido da loja
            )
        except Store.DoesNotExist:
            return OrderItem.objects.none()

    def perform_create(self, serializer):
        """Associa o item ao pedido pai da URL."""
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
    queryset = Category.objects.filter(is_active=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] # Todos podem ver
    lookup_field = 'slug'

    def get_permissions(self):
        """Qualquer um pode ver, apenas staff pode editar."""
        if self.action in ['list', 'retrieve', 'products']:
            return [AllowAny()]
        return [IsAuthenticated(),] # Idealmente: IsAdminUser

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Retorna todos os produtos ativos desta categoria."""
        category = self.get_object()
        
        # CORREÇÃO 3: 'product_categories__category' mudou para 'categories'
        products = Product.objects.filter(
            categories=category,
            is_active=True
        ).select_related('store').prefetch_related('variants')

        # Filtros de Preço
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        # CORREÇÃO 4: 'price' está em 'variants', não em 'product'
        if min_price:
            try:
                products = products.filter(variants__price__gte=Decimal(min_price))
            except Exception: pass
        if max_price:
            try:
                products = products.filter(variants__price__lte=Decimal(max_price))
            except Exception: pass

        # Garante que não haja duplicatas se um produto corresponder a múltiplos filtros
        serializer = ProductSerializer(products.distinct(), many=True, context={'request': request})
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Reviews (aninhado em /products/{product_pk}/reviews/)
    """
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Qualquer um pode ver, apenas autenticados podem criar."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()] # Adicionar permissão de "dono" para update/delete

    def get_queryset(self):
        """
        CORREÇÃO 2: Filtra reviews baseado na URL aninhada (product_pk).
        """
        qs = super().get_queryset().filter(
            product_id=self.kwargs.get('product_pk')
        ).select_related('user', 'product')
        
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        """Define o usuário, o produto da URL e verifica se foi comprado."""
        user = self.request.user
        try:
            product = Product.objects.get(pk=self.kwargs.get('product_pk'))
        except Product.DoesNotExist:
             raise ValidationError("Produto não encontrado.")

        # CORREÇÃO 5: 'OrderItem' não tem 'product', tem 'variant__product'
        has_purchased = OrderItem.objects.filter(
            Q(order__customer_email=user.email) | Q(order__customer_name=user.username), # Suposição de lógica de cliente
            variant__product=product,
            order__payment_status='paid'
        ).exists()

        try:
            serializer.save(user=user, product=product, is_verified_purchase=has_purchased)
        except IntegrityError:
            raise ValidationError({"detail": "Você já avaliou este produto."})


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Cupons (apenas para donos de loja/admin).
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated] # Idealmente: IsAdminUser ou Dono da Loja

    def get_queryset(self):
        """Admin vê tudo, donos de loja (se tivessem) veriam os seus."""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Coupon.objects.all()
        # Lógica de cupom por loja (se existir)
        # return Coupon.objects.filter(store=self.request.user.store)
        return Coupon.objects.none() # Não-staff não deve ver

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_coupon(self, request):
        """Valida um cupom para um cliente no checkout."""
        code = request.data.get('code')
        total = request.data.get('total', 0)

        if not code:
            return Response({'error': 'Código do cupom é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        if not total or Decimal(str(total)) <= 0:
             return Response({'error': 'Valor total é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code__iexact=code) # __iexact é melhor
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
    ViewSet para a Lista de Desejos (Wishlist) do usuário.
    """
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Usuários veem apenas sua própria lista."""
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        """Define o usuário automaticamente."""
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
             raise ValidationError({"detail": "Este item já está na sua lista de desejos."})

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Adiciona ou remove um produto da lista de desejos."""
        product_id = request.data.get('product') # Serializer espera 'product'

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