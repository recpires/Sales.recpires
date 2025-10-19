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
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Evita duplicar a mesma combinação cor+tamanho para o mesmo produto
            models.UniqueConstraint(
                fields=['product', 'color', 'size'],
                name='uniq_product_color_size',
                condition=Q(color__isnull=False) & Q(size__isnull=False),
            )
        ]

    def __str__(self):
        attrs = []
        if self.color:
            attrs.append(self.color)
        if self.size:
            attrs.append(self.size)
        attrs_str = ' / '.join(attrs) if attrs else 'default'
        return f"{self.product.name} - {attrs_str} ({self.sku})"


class Order(models.Model):
    """Model for customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
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

    def save(self, *args, **kwargs):
        """Auto-define preço unitário e valida vínculo produto/variante"""
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
        super().save(*args, **kwargs)
