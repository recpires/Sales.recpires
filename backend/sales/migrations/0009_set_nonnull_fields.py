"""Set Product.store and OrderItem.variant to non-nullable.

This is a manual migration created because the automatic makemigrations prompts
for interactive defaults in some environments. We already backfilled missing
values in 0008_backfill_and_set_nonnull, so it's safe to set null=False.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_backfill_and_set_nonnull'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='products', to='sales.store', null=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='variant',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='order_items', to='sales.productvariant', null=False),
        ),
    ]
