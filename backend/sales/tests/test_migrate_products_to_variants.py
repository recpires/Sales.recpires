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
        # Insert a legacy product row (DB columns price/stock/sku exist in migrations)
        from django.db import connection
        now = None
        with connection.cursor() as cursor:
            from django.utils import timezone
            now = timezone.now()
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P1', '', '10.00', 5, 'SKU1', 1, now, now, self.store.pk, 'black', 'M']
            )
            product_id = cursor.lastrowid
        out = StringIO()
        call_command('migrate_products_to_variants', '--dry-run', stdout=out)
        self.assertIn('DRY RUN', out.getvalue())
        # no variants should have been created in dry-run
        self.assertEqual(ProductVariant.objects.count(), 0)

    def test_creates_variant_for_product_without_variants(self):
        # legacy product row
        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P2', '', '15.00', 3, 'SKU2', 1, now, now, self.store.pk, 'black', 'M']
            )
            product_id = cursor.lastrowid
        out = StringIO()
        call_command('migrate_products_to_variants', stdout=out)
        # a single variant should be created for the legacy product
        self.assertEqual(ProductVariant.objects.count(), 1)
        v = ProductVariant.objects.first()
        self.assertEqual(v.price, 15.00)
        self.assertEqual(v.stock, 3)

    def test_resolve_sku_append_id(self):
        # create existing variant SKU conflict
        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P3', '', '20.00', 2, None, 1, now, now, self.store.pk, 'black', 'M']
            )
            p1_id = cursor.lastrowid
        # create existing variant SKU conflict
        ProductVariant.objects.create(product_id=p1_id, sku='X', price=20.0, stock=2)

        # another product with same sku
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P4', '', '25.00', 4, 'X', 1, now, now, self.store.pk, 'black', 'M']
            )
            p2_id = cursor.lastrowid
        out = StringIO()
        call_command('migrate_products_to_variants', '--resolve-skus=append-id', stdout=out)
        # ensure a new variant was created with appended id
        self.assertTrue(ProductVariant.objects.filter(sku__contains='X-').exists())

    def test_resolve_sku_skip(self):
        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P5', '', '30.00', 1, None, 1, now, now, self.store.pk, 'black', 'M']
            )
            p1_id = cursor.lastrowid
        ProductVariant.objects.create(product_id=p1_id, sku='Y', price=30.0, stock=1)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P6', '', '35.00', 2, 'Y', 1, now, now, self.store.pk, 'black', 'M']
            )
            p2_id = cursor.lastrowid
        out = StringIO()
        call_command('migrate_products_to_variants', '--resolve-skus=skip', stdout=out)
        # no new variant for p2
        self.assertEqual(ProductVariant.objects.filter(product_id=p2_id).count(), 0)

    def test_resolve_sku_fail_raises(self):
        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P7', '', '40.00', 1, None, 1, now, now, self.store.pk, 'black', 'M']
            )
            p1_id = cursor.lastrowid
        ProductVariant.objects.create(product_id=p1_id, sku='Z', price=40.0, stock=1)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P8', '', '45.00', 2, 'Z', 1, now, now, self.store.pk, 'black', 'M']
            )
            p2_id = cursor.lastrowid
        with self.assertRaises(Exception):
            call_command('migrate_products_to_variants', '--resolve-skus=fail')

    def test_clear_product_fields(self):
        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['P9', '', '50.00', 6, 'CLEAN', 1, now, now, self.store.pk, 'black', 'M']
            )
            p_id = cursor.lastrowid
        out = StringIO()
        call_command('migrate_products_to_variants', '--clear-product-fields', stdout=out)
        v = ProductVariant.objects.filter(product_id=p_id).first()
        self.assertIsNotNone(v)
        # After clearing product fields the DB product row should have sku NULL and stock 0
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT sku, stock FROM sales_product WHERE id=%s", [p_id])
            row = cursor.fetchone()
        self.assertIsNone(row[0])
        self.assertEqual(row[1], 0)
