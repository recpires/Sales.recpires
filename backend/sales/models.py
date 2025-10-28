from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models import Q, Avg, F
from django.utils import timezone
import uuid

# --- Model de Loja (sem alterações) ---
class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store', verbose_name="Dono")
    name = models.CharField(max_length=200, verbose_name="Nome da Loja")
    description = models.TextField(blank=True, verbose_name="Descrição")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    address = models.TextField(blank=True, verbose_name="Endereço")
    is_active = models.BooleanField(default=True, verbose_name="Ativa?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

# --- Model de Categoria (sem alterações) ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Descrição")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Imagem")
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children',
        null=True, blank=True, verbose_name="Categoria Pai"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['name']
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name

# --- Model de Produto (Principal) ---
class Product(models.Model):
    # Choices movidos para fora para facilitar referência, mas podem ficar aqui.
    COLOR_CHOICES = [
        ('red', 'Vermelho'), ('blue', 'Azul'), ('green', 'Verde'), ('black', 'Preto'),
        ('white', 'Branco'), ('yellow', 'Amarelo'), ('pink', 'Rosa'), ('purple', 'Roxo'),
        ('orange', 'Laranja'), ('gray', 'Cinza'),
    ]
    SIZE_CHOICES = [
        ('XS', 'Extra Pequeno'), ('S', 'Pequeno'), ('M', 'Médio'), ('L', 'Grande'),
        ('XL', 'Extra Grande'), ('XXL', 'Extra Extra Grande'),
        ('33', '33'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'),
        ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name="Loja")
    name = models.CharField(max_length=200, verbose_name="Nome do Produto")
    description = models.TextField(blank=True, verbose_name="Descrição")
    categories = models.ManyToManyField(Category, related_name='products', blank=True, verbose_name="Categorias")
    is_active = models.BooleanField(default=True, verbose_name="Ativo?")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagem Principal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name

    # Método auxiliar (opcional, mas conveniente)
    def adicionar_variacao(self, cor, tamanho, quantidade, preco, modelo='', sku=None):
        if not sku:
            sku = f"{self.name[:3].upper()}-{str(cor)[:3].upper()}-{tamanho}-{uuid.uuid4().hex[:6]}"
        
        # Este método USA ProductVariant.objects.create internamente!
        return ProductVariant.objects.create(
            product=self, color=cor, size=tamanho, model=modelo,
            stock=quantidade, price=preco, sku=sku
        )

    # ... (demais propriedades como total_stock, average_rating, review_count) ...
    @property
    def total_stock(self):
        return sum(v.stock for v in self.variants.filter(is_active=True))

    @property
    def average_rating(self):
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


# --- Model de Variação (Cor, Tamanho, Estoque, Preço) ---
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants',
        verbose_name="Produto Principal"
    )
    sku = models.CharField(
        max_length=100, unique=True, verbose_name="SKU",
        help_text="Identificador único para esta variação específica."
    )
    color = models.CharField(
        max_length=20, choices=Product.COLOR_CHOICES, verbose_name="Cor",
        help_text="A cor desta variação."
    )
    size = models.CharField(
        max_length=10, choices=Product.SIZE_CHOICES, verbose_name="Tamanho",
        help_text="O tamanho desta variação."
    )
    model = models.CharField(
        max_length=50, blank=True, default='', verbose_name="Modelo",
        help_text="Ex: 'Manga Longa', 'Slim Fit' (opcional)."
    )
    stock = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], verbose_name="Estoque",
        help_text="Quantidade disponível desta variação específica."
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preço", help_text="Preço desta variação específica."
    )
    image = models.ImageField(
        upload_to='products/variants/', blank=True, null=True, verbose_name="Imagem da Variação",
        help_text="Imagem específica para esta variação (opcional, usará a do produto principal se vazia)."
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['product__name', 'color', 'size'] # Melhor ordenação padrão
        verbose_name = "Variação de Produto"
        verbose_name_plural = "Variações de Produtos"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size', 'model'],
                name='uniq_product_color_size_model',
            ),
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name='check_stock_non_negative'
            )
        ]

    def __str__(self):
        modelo_str = f" | {self.model}" if self.model else ""
        return f"{self.product.name} - {self.get_color_display()} | {self.size}{modelo_str} | R$ {self.price} (Est: {self.stock})"

    def __repr__(self):
        attrs = [self.get_color_display(), self.get_size_display()]
        if self.model: attrs.append(self.model)
        attrs_str = ' / '.join(filter(None, attrs))
        return f"<Variant: {self.product.name} - {attrs_str} ({self.sku})>"

# --- Models de Pedido, Review, Coupon, Wishlist (sem alterações necessárias para esta questão) ---
# ... (seu código para Order, OrderItem, OrderStatusUpdate, Review, Coupon, Wishlist) ...
# (Colei eles aqui para referência, mas não foram modificados)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'), ('processing', 'Processando'), ('awaiting_delivery', 'Aguardando entrega'),
        ('out_for_delivery', 'Saiu para entrega'), ('delivered', 'Entregue'), ('cancelled', 'Cancelado'),
        ('shipped', 'Enviado'),
    ]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True, verbose_name="Loja")
    customer_name = models.CharField(max_length=200, verbose_name="Nome do Cliente")
    customer_email = models.EmailField(verbose_name="E-mail do Cliente")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone do Cliente")
    shipping_address = models.TextField(verbose_name="Endereço de Entrega")
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="Cupom")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor do Desconto")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    payment_method = models.CharField(max_length=20, choices=[('online', 'Online'), ('cod', 'Pagamento na entrega')], default='online', verbose_name="Método Pagto")
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pendente'), ('paid', 'Pago'), ('failed', 'Falhou')], default='pending', verbose_name="Status Pagto")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Pago em")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer_name}"

    def calculate_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        # Aplicar desconto do cupom se houver
        if self.coupon:
             discount = self.coupon.calculate_discount(total)
             self.discount_amount = discount
             total -= discount
        else:
            self.discount_amount = 0
        self.total_amount = max(total, Decimal(0)) # Garante que não fique negativo
        self.save(update_fields=['total_amount', 'discount_amount', 'updated_at'])
        return self.total_amount

    def set_status(self, new_status: str, note: str | None = None, automatic: bool = True):
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError("Status inválido.")
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        OrderStatusUpdate.objects.create(
            order=self, status=new_status, note=note or '', is_automatic=automatic,
        )
        # Aqui você pode adicionar lógica para enviar notificações, etc.
        return self

    def mark_cod_paid(self):
        if self.payment_method != 'cod':
            raise ValueError("Este pedido não é de pagamento na entrega.")
        self.payment_status = 'paid'
        self.paid_at = timezone.now()
        self.save(update_fields=['payment_status', 'paid_at', 'updated_at'])
        return self


class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates', verbose_name="Pedido")
    status = models.CharField(max_length=20, verbose_name="Novo Status")
    note = models.TextField(blank=True, default='', verbose_name="Nota")
    is_automatic = models.BooleanField(default=True, verbose_name="Automático?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Atualização de Status do Pedido"
        verbose_name_plural = "Atualizações de Status dos Pedidos"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Pedido")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name='order_items', verbose_name="Variação"
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Quantidade")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário (Snapshot)")

    @property
    def product(self):
        return self.variant.product

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"

    def __str__(self):
        return f"{self.quantity}x {self.variant.product.name} ({self.variant.sku}) no Pedido #{self.order.id}"

    def get_subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.unit_price = self.variant.price # Snapshot do preço
        
        previous_qty = 0
        if not is_new:
            try:
                previous_qty = OrderItem.objects.get(pk=self.pk).quantity
            except OrderItem.DoesNotExist: pass
        delta = self.quantity - previous_qty

        if delta > 0:
            variant_stock = ProductVariant.objects.select_for_update().get(pk=self.variant.pk).stock
            if delta > variant_stock:
                raise ValueError(f"Estoque insuficiente ({variant_stock}) para {self.variant.sku}.")

        super().save(*args, **kwargs)

        if delta != 0:
            ProductVariant.objects.filter(pk=self.variant.pk).update(stock=F('stock') - delta)

    def delete(self, *args, **kwargs):
        qty = self.quantity
        variant_pk = self.variant.pk
        super().delete(*args, **kwargs)
        # Devolve estoque atomicamente
        ProductVariant.objects.filter(pk=variant_pk).update(stock=F('stock') + qty)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Produto")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Usuário")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Nota (1-5)")
    title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    comment = models.TextField(blank=True, verbose_name="Comentário")
    is_verified_purchase = models.BooleanField(default=False, verbose_name="Compra Verificada?")
    is_approved = models.BooleanField(default=True, verbose_name="Aprovado?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [('percentage', 'Percentual'), ('fixed', 'Valor Fixo')]
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descrição")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage', verbose_name="Tipo Desconto")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Valor Desconto")
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name="Compra Mínima")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Desconto Máximo")
    usage_limit = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)], verbose_name="Limite de Usos")
    usage_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Vezes Usado")
    valid_from = models.DateTimeField(verbose_name="Válido De")
    valid_until = models.DateTimeField(verbose_name="Válido Até")
    is_active = models.BooleanField(default=True, verbose_name="Ativo?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        if not self.is_active: return False, "Cupom inativo"
        if now < self.valid_from: return False, "Cupom ainda não válido"
        if now > self.valid_until: return False, "Cupom expirado"
        if self.usage_limit and self.usage_count >= self.usage_limit: return False, "Limite de uso atingido"
        return True, "Cupom válido"

    def calculate_discount(self, total_amount):
        if self.discount_type == 'percentage':
            discount = total_amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else: discount = self.discount_value
        return min(discount, total_amount) # Não pode descontar mais que o total

    def increment_usage(self):
        """ Incrementa o contador de uso atomicamente """
        self.usage_count = F('usage_count') + 1
        self.save(update_fields=['usage_count'])


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Usuário")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Produto")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Adicionado em")

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']
        verbose_name = "Item da Lista de Desejos"
        verbose_name_plural = "Lista de Desejos"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"