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
    """Produto principal (container de variações) - NÃO armazena preço/estoque/cor/tamanho"""
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
        ('33', '33'), ('34', '34'), ('35', '35'), ('36', '36'),
        ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'),
        ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def adicionar_variacao(self, cor, tamanho, quantidade, preco, modelo='', sku=None):
        """
        Adiciona uma nova variação ao produto.
        Exemplo: camisa.adicionar_variacao("Azul", "M", 10, 50.00)
        """
        if not sku:
            # Gera SKU automaticamente se não fornecido
            import uuid
            sku = f"{self.name[:3].upper()}-{cor[:3].upper()}-{tamanho}-{uuid.uuid4().hex[:6]}"
        
        return ProductVariant.objects.create(
            product=self,
            color=cor,
            size=tamanho,
            model=modelo,
            stock=quantidade,
            price=preco,
            sku=sku
        )

    def listar_variacoes(self):
        """
        Retorna QuerySet de variações ativas.
        Para imprimir: for v in produto.listar_variacoes(): print(v)
        """
        return self.variants.filter(is_active=True)

    @property
    def total_stock(self):
        """Soma o estoque de todas as variações ativas."""
        return sum(v.stock for v in self.variants.filter(is_active=True))


class ProductVariant(models.Model):
    """
    Variação do produto (cor, tamanho, modelo, quantidade, preço).
    TODA venda é feita através de uma variação específica.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20, choices=Product.COLOR_CHOICES)
    size = models.CharField(max_length=10, choices=Product.SIZE_CHOICES)
    model = models.CharField(max_length=50, blank=True, default='')
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size', 'model'],
                name='uniq_product_color_size_model',
            )
        ]

    def __str__(self):
        """Formato: Azul | M | Qtd: 10 | R$ 50.00"""
        modelo_str = f" | {self.model}" if self.model else ""
        return f"{self.get_color_display()} | {self.size}{modelo_str} | Qtd: {self.stock} | R$ {self.price}"

    def __repr__(self):
        return f"<Variacao: {self.product.name} - {self.color} {self.size}>"
