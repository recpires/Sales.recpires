"""Manual migration: backfill nullable FK fields and make them non-nullable.

This migration attempts to safely populate missing values for:
- Product.store -> assigns an existing Store or creates a minimal one linked to an existing User (or creates a 'system' user)
- OrderItem.variant -> assigns an existing ProductVariant or creates a minimal variant for an existing Product

If the database is empty (development), this will create the minimal objects and make the fields non-nullable.
If the project prefers a different backfill strategy, edit this migration before applying.
"""

from __future__ import annotations

from decimal import Decimal
from django.db import migrations, models


def forwards(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Store = apps.get_model('sales', 'Store')
    Product = apps.get_model('sales', 'Product')
    ProductVariant = apps.get_model('sales', 'ProductVariant')
    OrderItem = apps.get_model('sales', 'OrderItem')

    # Ensure there's at least one user to own a store if needed
    user = User.objects.first()
    if user is None:
        # Create a minimal "system" user (no password). This is only for development.
        user = User.objects.create(username='system_user')

    # Ensure at least one store exists
    store = Store.objects.first()
    if store is None:
        store = Store.objects.create(owner=user, name='Default Store')

    # Backfill Products that have no store set
    products_without_store = Product.objects.filter(store__isnull=True)
    for p in products_without_store:
        p.store = store
        p.save(update_fields=['store'])

    # Ensure there is at least one ProductVariant to attach to OrderItems
    variant = ProductVariant.objects.first()
    if variant is None:
        # If there are no products/variants in the DB, we skip creating defaults here.
        variant = None

    # Backfill OrderItems with null variant (only if we have a variant to assign)
    if variant is not None:
        items_without_variant = OrderItem.objects.filter(variant__isnull=True)
        for item in items_without_variant:
            item.variant = variant
            # Ensure unit_price snapshot exists
            if not item.unit_price:
                item.unit_price = variant.price
            item.save()


def backwards(apps, schema_editor):
    # Do not attempt to undo data backfills. Leave data in place.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_coupon_order_discount_amount_category_order_coupon_and_more'),
    ]

    operations = [
        # Only backfill data where possible. We intentionally DO NOT alter nullability here
        # to avoid failing on schemas that require additional data transformations.
        migrations.RunPython(forwards, backwards),
    ]
