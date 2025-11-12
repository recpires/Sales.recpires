from django.core.management.base import BaseCommand
from sales.models import Product, Store
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Diagnóstico completo dos produtos e suas relações'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('DIAGNÓSTICO DE PRODUTOS'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # 1. Estatísticas gerais
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        inactive_products = Product.objects.filter(is_active=False).count()

        self.stdout.write('\n📊 ESTATÍSTICAS GERAIS:')
        self.stdout.write(f'  Total de produtos: {total_products}')
        self.stdout.write(f'  Produtos ativos: {active_products}')
        self.stdout.write(f'  Produtos inativos: {inactive_products}')

        # 2. Produtos SEM loja (problema principal)
        products_no_store = Product.objects.filter(store__isnull=True)
        count_no_store = products_no_store.count()

        self.stdout.write('\n🚨 PRODUTOS SEM LOJA (CAUSA DO ERRO 500):')
        if count_no_store > 0:
            self.stdout.write(self.style.ERROR(f'  ⚠ {count_no_store} produtos SEM loja'))
            self.stdout.write('  Detalhes:')
            for p in products_no_store[:10]:  # Mostra até 10
                self.stdout.write(f'    - ID {p.id}: {p.name} (ativo: {p.is_active})')
            if count_no_store > 10:
                self.stdout.write(f'    ... e mais {count_no_store - 10} produtos')
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Todos os produtos têm loja associada'))

        # 3. Produtos COM loja
        products_with_store = Product.objects.filter(store__isnull=False)
        count_with_store = products_with_store.count()

        self.stdout.write('\n✅ PRODUTOS COM LOJA:')
        self.stdout.write(f'  Total: {count_with_store}')

        # 4. Distribuição por loja
        self.stdout.write('\n🏪 DISTRIBUIÇÃO POR LOJA:')
        stores = Store.objects.all()
        for store in stores:
            product_count = Product.objects.filter(store=store).count()
            self.stdout.write(f'  - {store.name} ({store.owner.username}): {product_count} produtos')

        # 5. Produtos com problemas de imagem
        products_no_image = Product.objects.filter(image='').count()
        self.stdout.write('\n🖼️ IMAGENS:')
        self.stdout.write(f'  Produtos sem imagem: {products_no_image}')

        # 6. Produtos sem variantes
        products_without_variants = Product.objects.filter(variants__isnull=True).distinct()
        count_no_variants = products_without_variants.count()

        self.stdout.write('\n📦 VARIANTES:')
        self.stdout.write(f'  Produtos sem variantes: {count_no_variants}')

        # 7. Recomendações
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.HTTP_INFO('RECOMENDAÇÕES:'))
        self.stdout.write('=' * 60)

        if count_no_store > 0:
            self.stdout.write(self.style.WARNING(
                '\n⚠ AÇÃO NECESSÁRIA: Produtos sem loja causam erro 500!'
            ))
            self.stdout.write('  Opções de correção:')
            self.stdout.write('  1. Desativar produtos órfãos:')
            self.stdout.write('     python manage.py check_products_without_store --fix')
            self.stdout.write('  2. Associar a uma loja manualmente no Django Admin')
            self.stdout.write('  3. Deletar produtos órfãos (não recomendado)')
        else:
            self.stdout.write(self.style.SUCCESS(
                '\n✓ Nenhum problema crítico encontrado!'
            ))

        # 8. Simulação do erro
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.HTTP_INFO('SIMULAÇÃO DO ERRO:'))
        self.stdout.write('=' * 60)

        if count_no_store > 0:
            self.stdout.write(self.style.ERROR(
                '\nQuando um usuário acessa /api/products/, o sistema:'
            ))
            self.stdout.write('  1. Busca produtos ativos (inclui produtos sem loja)')
            self.stdout.write('  2. Tenta serializar cada produto')
            self.stdout.write('  3. No ProductSerializer, tenta acessar: product.store.name')
            self.stdout.write('  4. Se store=null, ocorre: AttributeError: "NoneType" object has no attribute "name"')
            self.stdout.write('  5. Django retorna: HTTP 500 Internal Server Error')
            self.stdout.write(self.style.SUCCESS(
                '\n✓ CORREÇÃO APLICADA: Agora usa get_store_name() que verifica se store existe'
            ))
