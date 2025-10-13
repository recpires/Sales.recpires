from django.test import TestCase
from django.core.management import call_command
from sales.models import Product, ProductVariant, Store
from django.contrib.auth.models import User
from io import StringIO


class MigrateProductsToVariantsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        self.store = Store.objects.create(owner=self.user, name='Loja')

    def test_dry_run_does_not_create_variants(self):
        p = Product.objects.create(store=self.store, name='P1', price=10.0, stock=5, sku='SKU1')
        out = StringIO()
        call_command('migrate_products_to_variants', '--dry-run', stdout=out)
        self.assertIn('DRY RUN', out.getvalue())
        self.assertEqual(ProductVariant.objects.count(), 0)

    def test_creates_variant_for_product_without_variants(self):
        p = Product.objects.create(store=self.store, name='P2', price=15.0, stock=3, sku='SKU2')
        out = StringIO()
        call_command('migrate_products_to_variants', stdout=out)
        self.assertEqual(ProductVariant.objects.count(), 1)
        v = ProductVariant.objects.first()
        self.assertEqual(v.price, p.price)
        self.assertEqual(v.stock, p.stock)

    def test_resolve_sku_append_id(self):
        # create existing variant SKU conflict
        p1 = Product.objects.create(store=self.store, name='P3', price=20.0, stock=2, sku='X')
        ProductVariant.objects.create(product=p1, sku='X', price=20.0, stock=2)

        # another product with same sku
        p2 = Product.objects.create(store=self.store, name='P4', price=25.0, stock=4, sku='X')
        out = StringIO()
        call_command('migrate_products_to_variants', '--resolve-skus=append-id', stdout=out)
        # ensure a new variant was created with appended id
        self.assertTrue(ProductVariant.objects.filter(sku__contains='X-').exists())

    def test_resolve_sku_skip(self):
        p1 = Product.objects.create(store=self.store, name='P5', price=30.0, stock=1, sku='Y')
        ProductVariant.objects.create(product=p1, sku='Y', price=30.0, stock=1)

        p2 = Product.objects.create(store=self.store, name='P6', price=35.0, stock=2, sku='Y')
        out = StringIO()
        call_command('migrate_products_to_variants', '--resolve-skus=skip', stdout=out)
        # no new variant for p2
        self.assertEqual(ProductVariant.objects.filter(product=p2).count(), 0)

    def test_resolve_sku_fail_raises(self):
        p1 = Product.objects.create(store=self.store, name='P7', price=40.0, stock=1, sku='Z')
        ProductVariant.objects.create(product=p1, sku='Z', price=40.0, stock=1)

        p2 = Product.objects.create(store=self.store, name='P8', price=45.0, stock=2, sku='Z')
        with self.assertRaises(Exception):
            call_command('migrate_products_to_variants', '--resolve-skus=fail')

    def test_clear_product_fields(self):
        p = Product.objects.create(store=self.store, name='P9', price=50.0, stock=6, sku='CLEAN')
        out = StringIO()
        call_command('migrate_products_to_variants', '--clear-product-fields', stdout=out)
        v = ProductVariant.objects.filter(product=p).first()
        self.assertIsNotNone(v)
        p.refresh_from_db()
        self.assertIsNone(p.sku)
        self.assertEqual(p.stock, 0)
