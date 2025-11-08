from django.core.management.base import BaseCommand
from sales.models import Product, Store


class Command(BaseCommand):
    help = 'Verifica e lista produtos sem loja associada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Associa produtos órfãos a uma loja padrão ou os desativa',
        )

    def handle(self, *args, **options):
        # Busca produtos sem loja
        products_without_store = Product.objects.filter(store__isnull=True)
        count = products_without_store.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                '✓ Nenhum produto sem loja encontrado!'
            ))
            return

        self.stdout.write(self.style.WARNING(
            f'⚠ Encontrados {count} produto(s) sem loja associada:'
        ))

        for product in products_without_store:
            self.stdout.write(
                f'  - ID: {product.id} | Nome: {product.name} | Ativo: {product.is_active}'
            )

        if options['fix']:
            self.stdout.write('\nAplicando correções...')

            # Opção 1: Desativar produtos sem loja
            products_without_store.update(is_active=False)
            self.stdout.write(self.style.SUCCESS(
                f'✓ {count} produto(s) desativado(s)'
            ))

            # Opção 2: Associar a uma loja padrão (descomentar se preferir)
            # default_store = Store.objects.first()
            # if default_store:
            #     products_without_store.update(store=default_store)
            #     self.stdout.write(self.style.SUCCESS(
            #         f'✓ {count} produto(s) associado(s) à loja: {default_store.name}'
            #     ))
            # else:
            #     self.stdout.write(self.style.ERROR('✗ Nenhuma loja disponível'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\nPara corrigir, execute: python manage.py check_products_without_store --fix'
                )
            )
