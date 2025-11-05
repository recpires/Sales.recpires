from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal


# --- ATTRIBUTE MODELS (for flexible product attributes) ---

class Attribute(models.Model):
    """Dynamic attributes for products (e.g., Color, Size, Material)"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """Values for attributes (e.g., Red, Blue for Color attribute)"""
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['attribute__name', 'value']
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


# --- CATEGORY MODEL ---

class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Price and stock can be null if product has variants
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)

    # Legacy category field - will be replaced by M2M categories
    category = models.CharField(max_length=100, blank=True)

    # Many-to-Many relationships
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    variant_attributes = models.ManyToManyField(Attribute, related_name='products', blank=True,
                                                help_text="Attributes used for product variants (e.g., Color, Size)")

    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        """Calculate total stock from all variants"""
        if self.variants.exists():
            return sum(v.stock for v in self.variants.all())
        return self.stock or 0

    @property
    def average_rating(self):
        """Calculate average rating from approved reviews"""
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            total = sum(r.rating for r in approved_reviews)
            return round(total / approved_reviews.count(), 1)
        return None

    @property
    def review_count(self):
        """Count of approved reviews"""
        return self.reviews.filter(is_approved=True).count()


class ProductVariant(models.Model):
    """Variants for a product (different size/color/price/sku/stock)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    # Variant name for display (e.g., "Size M, Color Blue")
    name = models.CharField(max_length=255, blank=True, help_text="Ex: Tamanho M, Cor Azul")

    # Many-to-Many relationship to AttributeValue for flexible variant attributes
    values = models.ManyToManyField(AttributeValue, related_name='variants', blank=True,
                                    help_text="Attribute values for this variant (e.g., Size: M, Color: Blue)")

    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        variant_name = self.name or " / ".join(str(v.value) for v in self.values.all())
        return f"{self.product.name} - {variant_name} ({self.sku})"


class Order(models.Model):
    """Order model with payment tracking and status updates"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('card', 'Card Payment'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Payment fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def calculate_total(self):
        """Calculate total from order items"""
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def set_status(self, new_status, note='', automatic=True):
        """Update order status and create status update record"""
        old_status = self.status
        self.status = new_status
        self.save()

        # Create status update record
        OrderStatusUpdate.objects.create(
            order=self,
            status=new_status,
            note=note,
            is_automatic=automatic
        )

        return old_status

    def mark_cod_paid(self):
        """Mark cash on delivery order as paid"""
        if self.payment_method == 'cod' and self.payment_status == 'pending':
            self.payment_status = 'paid'
            self.paid_at = timezone.now()
            self.save()
            return True
        return False


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name='order_items', verbose_name="Variação",
        null=True, blank=True
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
            elif self.product.price:
                self.unit_price = self.product.price
            else:
                self.unit_price = 0
        super().save(*args, **kwargs)


class OrderStatusUpdate(models.Model):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note = models.TextField(blank=True)
    is_automatic = models.BooleanField(default=True, help_text="Was this status change automatic?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order.id} - {self.status} at {self.created_at}"


class Review(models.Model):
    """Product reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"


class Coupon(models.Model):
    """Discount coupons"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(Decimal('0.01'))])
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                             help_text="Maximum discount for percentage coupons")
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Total times this coupon can be used")
    usage_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_value})"

    def is_valid(self):
        """Check if coupon is valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, amount):
        """Calculate discount for given amount"""
        if not self.is_valid():
            return 0

        if amount < self.min_purchase_amount:
            return 0

        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        else:  # fixed
            return min(self.discount_value, amount)


class Wishlist(models.Model):
    """User wishlist for products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')  # One product per user in wishlist

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"