from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


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
    # <--- ALTERAÇÃO: Removido COLOR_CHOICES e SIZE_CHOICES daqui, pois agora pertencem à variante

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # <--- ALTERAÇÃO: price e stock agora podem ser nulos, pois um produto
    # com variantes não terá preço/estoque principal.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True, 
        blank=True
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    
    # <--- ALTERAÇÃO: Adicionado campo 'category' que vem do formulário
    category = models.CharField(max_length=100, blank=True)
    
    # <--- ALTERAÇÃO: Removido 'color' e 'size' do produto principal
    # color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='black')
    # size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='M')
    
    # sku movido para ProductVariant to support multiple variants per product
    # Este SKU é o SKU principal/pai, que o formulário envia
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True) # Imagem principal
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """Variants for a product (different size/color/price/sku/stock)"""

    # <--- ALTERAÇÃO: Movido os CHOICES para cá, embora não sejam mais usados
    # diretamente, podem ser úteis no futuro.
    COLOR_CHOICES = [
        ('red', 'Vermelho'), ('blue', 'Azul'), ('green', 'Verde'), ('black', 'Preto'),
        ('white', 'Branco'), ('yellow', 'Amarelo'), ('pink', 'Rosa'), ('purple', 'Roxo'),
        ('orange', 'Laranja'), ('gray', 'Cinza'),
    ]
    SIZE_CHOICES = [
        ('XS', 'Extra Pequeno'), ('S', 'Pequeno'), ('M', 'Médio'), ('L', 'Grande'),
        ('XL', 'Extra Grande'), ('XXL', 'Extra Extra Grande'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # <--- ALTERAÇÃO: Adicionado campo 'name' para "Nome da Variante" (ex: "Tamanho M, Cor Azul")
    name = models.CharField(max_length=255, help_text="Ex: Tamanho M, Cor Azul")
    
    sku = models.CharField(max_length=100, unique=True) # SKU da variante
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # <--- ALTERAÇÃO: Removido 'color' e 'size' pois o formulário envia um 'name'
    # color = models.CharField(max_length=20, choices=COLOR_CHOICES, null=True, blank=True)
    # size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True) # Imagem específica da variante (opcional)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        # <--- ALTERAÇÃO: Atualizado para usar o novo campo 'name'
        return f"{self.product.name} - {self.name} ({self.sku})"


class Order(models.Model):
    # ... (Sem alterações necessárias aqui, seu modelo de Pedido está bom)
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'),
        ('delivered', 'Delivered'), ('cancelled', 'Cancelled'),
    ]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def calculate_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    # ... (Sem alterações necessárias aqui, seu modelo de Item de Pedido está bom)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name='order_items', verbose_name="Variação",
        null=True, blank=True  # Temporarily nullable during migration
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    def get_subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if not self.unit_price:
            if getattr(self, 'variant') and self.variant:
                self.unit_price = self.variant.price
            elif self.product.price: # <--- Pequena proteção caso o preço do produto seja nulo
                self.unit_price = self.product.price
            else:
                self.unit_price = 0 # Define um padrão se ambos forem nulos
        super().save(*args, **kwargs)