from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sales.models import Product, ProductVariant
from django.db.utils import IntegrityError
from django.db import connection


class Command(BaseCommand):
    help = 'Migrates existing Products into ProductVariants. Creates one default variant per product that has no variants.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not save changes, only show what would be done')
        parser.add_argument('--resolve-skus', choices=['append-id', 'skip', 'fail'], default='append-id',
                            help='How to resolve SKU uniqueness conflicts when creating variants')
        parser.add_argument('--clear-product-fields', action='store_true',
                            help='After creating variant, clear product.sku and set product.stock to 0')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        resolve = options['resolve_skus']
        clear_fields = options['clear_product_fields']

        products = Product.objects.all()
        total = products.count()
        created = 0
        skipped = 0
        failed = 0

        for p in products:
            # Skip products that already have variants
            if p.variants.exists():
                self.stdout.write(f"Skipping product {p.id} '{p.name}': already has variants")
                skipped += 1
                continue

            # Fetch legacy product fields directly from the DB when model no longer
            # exposes them (the current Product model was refactored).
            def _db_get(field):
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT {field} FROM sales_product WHERE id=%s", [p.id])
                    row = cursor.fetchone()
                return row[0] if row else None

            # Build SKU for variant (prefer DB column if present)
            sku_val = _db_get('sku')
            try:
                sku = sku_val if sku_val is not None else (p.sku if hasattr(p, 'sku') else None)
            except Exception:
                sku = sku_val
            if not sku:
                sku = f"PROD-{p.id}"

            # Resolve conflicts
            if ProductVariant.objects.filter(sku=sku).exists():
                if resolve == 'append-id':
                    sku = f"{sku}-{p.id}"
                elif resolve == 'skip':
                    self.stdout.write(f"Skipping product {p.id} '{p.name}': SKU conflict and --resolve-skus=skip")
                    skipped += 1
                    continue
                elif resolve == 'fail':
                    raise CommandError(f"SKU conflict for product {p.id} (sku={sku})")

            # Create variant inside transaction
            try:
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would create variant for product {p.id} with sku={sku}")
                    created += 1
                else:
                    with transaction.atomic():
                        # Read other legacy fields from DB if model doesn't expose them
                        price = _db_get('price') if _db_get('price') is not None else getattr(p, 'price', None)
                        color = _db_get('color') if _db_get('color') is not None else getattr(p, 'color', None)
                        size = _db_get('size') if _db_get('size') is not None else getattr(p, 'size', None)
                        stock = _db_get('stock') if _db_get('stock') is not None else getattr(p, 'stock', 0)
                        image = _db_get('image') if _db_get('image') is not None else getattr(p, 'image', None)
                        is_active = _db_get('is_active') if _db_get('is_active') is not None else getattr(p, 'is_active', True)

                        v = ProductVariant.objects.create(
                            product=p,
                            sku=sku,
                            price=price,
                            stock=stock,
                            image=image,
                            is_active=is_active,
                        )

                        if clear_fields:
                            # Update underlying DB row since Product model may no longer
                            # expose sku/stock fields after refactor.
                            with connection.cursor() as cursor:
                                cursor.execute("UPDATE sales_product SET sku=NULL, stock=0 WHERE id=%s", [p.id])

                        self.stdout.write(f"Created variant {v.sku} for product {p.id} ('{p.name}')")
                        created += 1
            except IntegrityError as e:
                self.stderr.write(f"Failed to create variant for product {p.id} ('{p.name}'): {e}")
                failed += 1

        self.stdout.write('\nSummary:')
        self.stdout.write(f'Total products scanned: {total}')
        self.stdout.write(f'Variants created: {created}')
        self.stdout.write(f'Skipped: {skipped}')
        self.stdout.write(f'Failed: {failed}')
