from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoreViewSet, ProductViewSet, ProductVariantViewSet, CategoryViewSet, CouponViewSet, 
    OrderViewSet,
    SupplierViewSet, PurchaseOrderViewSet # Novos ViewSets
)

# Cria um router para registrar ViewSets
router = DefaultRouter()

# Rotas de Vendas/E-commerce
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'variants', ProductVariantViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'orders', OrderViewSet)

# Rotas de Pedido de Compra (PO)
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')

urlpatterns = [
    # Inclui as rotas geradas pelo router (ViewSets)
    path('', include(router.urls)),
]

# Para fins de documentação, o URL base para pedidos de compra seria:
# /api/purchase-orders/
# E para fornecedores:
# /api/suppliers/