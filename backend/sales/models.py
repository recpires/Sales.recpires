from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F # Importação de F para expressões no banco de dados

# --- Store Models ---

class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store_profile', verbose_name=_("Usuário Proprietário"))
    name = models.CharField(max_length=255, verbose_name=_("Nome da Loja"))
    slug = models.SlugField(unique=True, max_length=255, verbose_name=_("Slug (URL Amigável)"))
    currency = models.CharField(max_length=10, default='BRL', verbose_name=_("Moeda"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Loja")
        verbose_name_plural = _("Lojas")

    def __str__(self):
        return self.name

class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories', verbose_name=_("Loja"))
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    
    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")
        unique_together = ('store', 'slug')

    def __str__(self):
        return f"{self.store.name} - {self.name}"


# --- Product Models ---

class Product(models.Model):
    """
    Modelo base do produto. Apenas contém informações genéricas do produto.
    Detalhes de preço, estoque, cor e tamanho foram movidos para ProductVariant.
    A migração 0005 já tratou dessa transição.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name=_("Loja"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_("Categoria"))
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(verbose_name=_("Descrição"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    
    # OBS: Campos 'color', 'size', 'sku', 'price', 'stock_quantity', 'image' removidos daqui.
    # Eles devem ser gerenciados através do modelo ProductVariant.

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Produto")
        verbose_name_plural = _("Produtos")
        unique_together = ('store', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.store.name})"

class ProductVariant(models.Model):
    """
    Representa uma variação específica de um produto (ex: Camisa Azul M).
    Contém os detalhes específicos de estoque, preço e atributos.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_("Produto"))
    sku = models.CharField(max_length=100, unique=True, db_index=True, verbose_name=_("SKU"))
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Cor"))
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Tamanho"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Preço"))
    stock_quantity = models.IntegerField(default=0, verbose_name=_("Quantidade em Estoque"))
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name=_("Imagem"))
    
    class Meta:
        verbose_name = _("Variante de Produto")
        verbose_name_plural = _("Variantes de Produtos")
        # Garante que não haja duplicidade de variante para o mesmo produto (ex: Camisa M Azul)
        unique_together = ('product', 'color', 'size') 

    def __str__(self):
        variant_details = f"{self.color or ''} {self.size or ''}".strip()
        if variant_details:
            return f"{self.product.name} - {variant_details}"
        return self.product.name

# --- Sales Order Models ---

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', _('Pendente')),
        ('PAID', _('Pago')),
        ('SHIPPED', _('Enviado')),
        ('DELIVERED', _('Entregue')),
        ('CANCELLED', _('Cancelado')),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', _('Cartão de Crédito')),
        ('BANK_TRANSFER', _('Transferência Bancária')),
        ('PIX', _('PIX')),
        ('CASH', _('Dinheiro')),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Loja"))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_("Usuário/Cliente"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING', verbose_name=_("Status"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Valor Total"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Valor do Desconto"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))
    
    # Detalhes de pagamento
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, verbose_name=_("Método de Pagamento"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Pago em"))
    
    # Detalhes do Cupom
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Cupom Aplicado"))
    
    # Endereço de entrega (simplificado)
    shipping_address = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("Endereço de Entrega"))
    
    class Meta:
        verbose_name = _("Pedido de Venda")
        verbose_name_plural = _("Pedidos de Venda")

    def __str__(self):
        return f"Pedido #{self.id} - {self.store.name} - Status: {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Pedido"))
    # Correção: O item deve se referir à ProductVariant, não ao Product.
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, verbose_name=_("Variante do Produto")) 
    quantity = models.IntegerField(verbose_name=_("Quantidade"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Preço na compra"))

    class Meta:
        verbose_name = _("Item do Pedido de Venda")
        verbose_name_plural = _("Itens do Pedido de Venda")

    def __str__(self):
        return f"{self.quantity}x {self.variant.product.name} ({self.variant.sku})"

class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates', verbose_name=_("Pedido"))
    old_status = models.CharField(max_length=50, verbose_name=_("Status Antigo"))
    new_status = models.CharField(max_length=50, verbose_name=_("Novo Status"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Data/Hora"))
    notes = models.TextField(blank=True, verbose_name=_("Notas"))

    class Meta:
        verbose_name = _("Atualização de Status do Pedido")
        verbose_plural = _("Atualizações de Status do Pedido")
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Pedido #{self.order.id}: {self.old_status} -> {self.new_status} em {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# --- Coupon Model ---

class Coupon(models.Model):
    TYPE_CHOICES = [
        ('PERCENTAGE', _('Porcentagem')),
        ('FIXED', _('Valor Fixo')),
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='coupons', verbose_name=_("Loja"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Código"))
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name=_("Tipo de Desconto"))
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Valor"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    valid_from = models.DateTimeField(verbose_name=_("Válido a Partir de"))
    valid_until = models.DateTimeField(verbose_name=_("Válido Até"))

    class Meta:
        verbose_name = _("Cupom de Desconto")
        verbose_name_plural = _("Cupons de Desconto")

    def __str__(self):
        return f"{self.code} ({self.type}: {self.value})"

# ----------------------------------------------------
#               NOVOS MODELOS PARA PO (Pedido de Ordem)
# ----------------------------------------------------

class Supplier(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='suppliers', verbose_name=_("Loja"))
    name = models.CharField(max_length=255, verbose_name=_("Nome do Fornecedor"))
    contact_name = models.CharField(max_length=255, blank=True, verbose_name=_("Pessoa de Contato"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Telefone"))
    address = models.TextField(blank=True, verbose_name=_("Endereço"))

    class Meta:
        verbose_name = _("Fornecedor")
        verbose_name_plural = _("Fornecedores")
        unique_together = ('store', 'name')

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', _('Rascunho')),
        ('PENDING', _('Aguardando Confirmação')),
        ('ORDERED', _('Pedido Confirmado')),
        ('RECEIVED_PARTIAL', _('Recebido Parcialmente')),
        ('RECEIVED_FULL', _('Recebido Totalmente')),
        ('CANCELLED', _('Cancelado')),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_orders', verbose_name=_("Loja"))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchase_orders', verbose_name=_("Fornecedor"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='DRAFT', verbose_name=_("Status"))
    order_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Data do Pedido"))
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name=_("Data de Entrega Prevista"))
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Custo Total"))
    notes = models.TextField(blank=True, verbose_name=_("Notas"))

    class Meta:
        verbose_name = _("Pedido de Compra (PO)")
        verbose_name_plural = _("Pedidos de Compra (PO)")
        ordering = ['-order_date']

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.name if self.supplier else 'N/A'} - Status: {self.status}"
    
    def calculate_total_cost(self):
        """Calcula e atualiza o custo total com base nos itens do PO."""
        # CORREÇÃO: Usando agregação do banco de dados para melhor performance
        aggregation = self.po_items.aggregate(
            total=Sum(F('ordered_quantity') * F('unit_cost'), output_field=models.DecimalField())
        )
        self.total_cost = aggregation.get('total') or 0.00
        self.save()

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='po_items', verbose_name=_("Pedido de Compra"))
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, verbose_name=_("Variante do Produto"))
    ordered_quantity = models.IntegerField(verbose_name=_("Quantidade Pedida"))
    received_quantity = models.IntegerField(default=0, verbose_name=_("Quantidade Recebida"))
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Custo Unitário"))
    
    # Campo calculado para o custo total deste item
    @property
    def total_cost(self):
        return self.ordered_quantity * self.unit_cost

    class Meta:
        verbose_name = _("Item do Pedido de Compra")
        verbose_name_plural = _("Itens do Pedido de Compra")
        unique_together = ('purchase_order', 'variant')

    def __str__(self):
        return f"{self.ordered_quantity}x {self.variant.product.name} ({self.variant.sku})"

# ----------------------------------------------------
#               SINAIS PÓS-SALVAMENTO
# ----------------------------------------------------

@receiver(post_save, sender=PurchaseOrder)
def update_stock_on_receipt(sender, instance, **kwargs):
    """
    Atualiza o custo total do PO no salvamento. A lógica de estoque é tratada no ViewSet.
    """
    if kwargs.get('created', False) == False and instance.status != 'DRAFT':
        instance.calculate_total_cost()
        
# A lógica de atualização de estoque (saída) para Order (venda) 
# é tratada diretamente no OrderSerializer.create.