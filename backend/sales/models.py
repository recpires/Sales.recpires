from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Q


class Store(models.Model):
    """Model for seller stores - each admin user has their own store"""
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.owner.username}"


class Product(models.Model):
    """Model for products/items available for sale"""
    COLOR_CHOICES = [
        ('red', 'Vermelho'),
        ('blue', 'Azul'),
        ('green', 'Verde'),
        ('black', 'Preto'),
        ('white', 'Branco'),
        ('yellow', 'Amarelo'),
        ('pink', 'Rosa'),
        ('purple', 'Roxo'),
        ('orange', 'Laranja'),
        ('gray', 'Cinza'),
    ]

    SIZE_CHOICES = [
        ('XS', 'Extra Pequeno'),
        ('S', 'Pequeno'),
        ('M', 'Médio'),
        ('L', 'Grande'),
        ('XL', 'Extra Grande'),
        ('XXL', 'Extra Extra Grande'),
        # Tamanhos de tênis (BR)
        ('33', '33'),
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='black')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='M')
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    # sku moved to ProductVariant to support multiple variants per product
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # adicionados: utilitários para variantes
    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def total_stock(self):
        if self.has_variants:
            return sum(v.stock for v in self.variants.filter(is_active=True))
        return self.stock


class ProductVariant(models.Model):
    """Variants for a product (different size/color/price/sku/stock)

    Each product can have multiple variants. Variant-level SKU and stock
    are stored here. If a product has no variants, the product-level fields
    (price/stock/sku) can still be used.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    color = models.CharField(max_length=20, choices=Product.COLOR_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=10, choices=Product.SIZE_CHOICES, null=True, blank=True)
    # novo atributo: modelo (ex.: "Cano médio", "Slim", etc.)
    model = models.CharField(max_length=50, null=True, blank=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Evita duplicar a mesma combinação (cor, tamanho, modelo) para o mesmo produto
            models.UniqueConstraint(
                fields=['product', 'color', 'size', 'model'],
                name='uniq_product_color_size_model',
                condition=Q(color__isnull=False) & Q(size__isnull=False) & Q(model__isnull=False),
            )
        ]

    def __str__(self):
        attrs = []
        if self.color:
            attrs.append(self.color)
        if self.size:
            attrs.append(self.size)
        if self.model:
            attrs.append(self.model)
        attrs_str = ' / '.join(attrs) if attrs else 'default'
        return f"{self.product.name} - {attrs_str} ({self.sku})"


class Order(models.Model):
    """Model for customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('awaiting_delivery', 'Aguardando entrega'),
        ('out_for_delivery', 'Saiu para entrega'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
        # compatibilidade com versões antigas
        ('shipped', 'Enviado'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    # pagamento
    payment_method = models.CharField(
        max_length=20,
        choices=[('online', 'Online'), ('cod', 'Pagamento na entrega')],
        default='online'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pendente'), ('paid', 'Pago'), ('failed', 'Falhou')],
        default='pending'
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def set_status(self, new_status: str, note: str | None = None, automatic: bool = True):
        """Atualiza status e registra histórico (base para notificações)."""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError("Status inválido.")
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        OrderStatusUpdate.objects.create(
            order=self,
            status=new_status,
            note=note or '',
            is_automatic=automatic,
        )
        return self

    def mark_cod_paid(self):
        """Registra pagamento realizado na entrega (apenas para COD)."""
        if self.payment_method != 'cod':
            raise ValueError("Este pedido não é de pagamento na entrega.")
        from django.utils import timezone
        self.payment_status = 'paid'
        self.paid_at = timezone.now()
        self.save(update_fields=['payment_status', 'paid_at', 'updated_at'])
        return self


class OrderStatusUpdate(models.Model):
    """Histórico de mudanças de status (usar para notificações)."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True, default='')
    is_automatic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Model for items in an order"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items',
        null=True,
        blank=True,
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.quantity * self.unit_price

    def _get_available_stock(self):
        if self.variant:
            return self.variant.stock
        return self.product.stock

    def save(self, *args, **kwargs):
        """Valida produto/variante, define preço e controla estoque."""
        # Variante deve pertencer ao mesmo produto
        if self.variant and self.variant.product_id != self.product_id:
            raise ValueError("A variação selecionada não pertence ao produto informado.")
        # Se o produto tem variantes, a variante é obrigatória
        if not self.variant and self.product.variants.exists():
            raise ValueError("Este produto possui variações. Selecione uma variação.")
        # Preferir preço da variante quando houver
        if not self.unit_price:
            if getattr(self, 'variant') and self.variant:
                self.unit_price = self.variant.price
            else:
                self.unit_price = self.product.price

        # Calcular delta de quantidade para ajustar estoque
        previous_qty = 0
        if self.pk:
            try:
                previous_qty = OrderItem.objects.get(pk=self.pk).quantity
            except OrderItem.DoesNotExist:
                previous_qty = 0
        delta = self.quantity - previous_qty

        # Verificar estoque ao aumentar a quantidade
        if delta > 0:
            available = self._get_available_stock()
            if delta > available:
                raise ValueError(f"Quantidade solicitada ({self.quantity}) excede o estoque disponível ({available}).")

        super().save(*args, **kwargs)

        # Ajustar estoque após salvar
        if delta != 0:
            if self.variant:
                self.variant.stock = models.F('stock') - delta
                self.variant.save(update_fields=['stock'])
                self.variant.refresh_from_db(fields=['stock'])
            else:
                self.product.stock = models.F('stock') - delta
                self.product.save(update_fields=['stock'])
                self.product.refresh_from_db(fields=['stock'])

    def delete(self, *args, **kwargs):
        """Devolve o estoque ao remover o item do pedido."""
        qty = self.quantity
        super().delete(*args, **kwargs)
        if self.variant:
            self.variant.stock = models.F('stock') + qty
            self.variant.save(update_fields=['stock'])
            self.variant.refresh_from_db(fields=['stock'])
        else:
            self.product.stock = models.F('stock') + qty
            self.product.save(update_fields=['stock'])
            self.product.refresh_from_db(fields=['stock'])
