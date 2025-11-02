import threading
from django.test import TransactionTestCase
from django.db import transaction, close_old_connections

from sales.models import Product, ProductVariant, Order, OrderItem, Store
from django.contrib.auth import get_user_model


class TestConcurrentOrders(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username='test_user')
        # Create a store (ORM) and then insert a Product row using raw SQL
        # because the migration schema includes columns removed from the model.
        self.store = Store.objects.create(owner=self.user, name='Test Store')

        from django.db import connection
        from django.utils import timezone
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sales_product (name, description, price, stock, sku, is_active, created_at, updated_at, store_id, color, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ['Concurrent Product', '', '1.00', 10, 'CONC-P', 1, now, now, self.store.pk, 'black', 'M']
            )
            product_id = cursor.lastrowid

        # Create a single variant with stock=1 to test contention
        self.variant = ProductVariant.objects.create(
            product_id=product_id, sku='CONC-1', price=10.00, stock=1
        )

    def _create_order_attempt(self, results, index, qty=1):
        # Ensure this thread uses a fresh DB connection
        close_old_connections()
        try:
            # Simulate the critical section of OrderItem.save(): lock the variant row and decrement stock
            with transaction.atomic():
                v = ProductVariant.objects.select_for_update().get(pk=self.variant.pk)
                if qty > v.stock:
                    raise ValueError(f"Estoque insuficiente ({v.stock}) para {v.sku}.")
                v.stock = v.stock - qty
                v.save()
            results[index] = 'ok'
        except Exception as e:
            results[index] = f'error: {e}'

    def test_two_concurrent_orders_only_one_succeeds(self):
        results = [None, None]

        t1 = threading.Thread(target=self._create_order_attempt, args=(results, 0, 1))
        t2 = threading.Thread(target=self._create_order_attempt, args=(results, 1, 1))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Exactly one should succeed and one should fail due to insufficient stock
        successes = [r for r in results if r == 'ok']
        errors = [r for r in results if r != 'ok']

        self.assertEqual(len(successes), 1, msg=f'should have exactly one success, got {results}')
        self.assertEqual(len(errors), 1, msg=f'should have exactly one error, got {results}')

        # Refresh variant from DB and ensure stock is 0
        v = ProductVariant.objects.get(pk=self.variant.pk)
        self.assertEqual(v.stock, 0)
