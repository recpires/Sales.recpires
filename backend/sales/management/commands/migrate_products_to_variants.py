from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sales.models import Product, ProductVariant
from django.db.utils import IntegrityError


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

            # Build SKU for variant
            sku = p.sku if p.sku else f"PROD-{p.id}"

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
                        v = ProductVariant.objects.create(
                            product=p,
                            sku=sku,
                            price=p.price,
                            color=p.color if p.color else None,
                            size=p.size if p.size else None,
                            stock=p.stock,
                            image=p.image,
                            is_active=p.is_active,
                        )

                        if clear_fields:
                            p.sku = None
                            p.stock = 0
                            p.save()

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
