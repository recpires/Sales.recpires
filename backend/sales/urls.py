from django.urls import path, include
# CORREÇÃO: Importar o 'nested' router
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ProductViewSet, OrderViewSet, OrderItemViewSet, StoreViewSet, ProductVariantViewSet,
    CategoryViewSet, ReviewViewSet, CouponViewSet, WishlistViewSet
)
from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ChangePasswordView
)

# 1. Crie o router principal (apenas para os "pais")
router = routers.DefaultRouter()
router.register('stores', StoreViewSet, basename='store')
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')
router.register('categories', CategoryViewSet, basename='category')
router.register('coupons', CouponViewSet, basename='coupon')
router.register('wishlist', WishlistViewSet, basename='wishlist')

# CORREÇÃO: Removidas as rotas globais para 'order-items', 'variants', e 'reviews'

# 2. Crie um router aninhado para /products/
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
# Isso cria: /products/{product_pk}/variants/
products_router.register('variants', ProductVariantViewSet, basename='product-variants')
# Isso cria: /products/{product_pk}/reviews/
products_router.register('reviews', ReviewViewSet, basename='product-reviews')

# 3. Crie um router aninhado para /orders/
orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')
# Isso cria: /orders/{order_pk}/items/
orders_router.register('items', OrderItemViewSet, basename='order-items')


urlpatterns = [
    # API routes (já prefixadas com 'api/' no core/urls.py)
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(orders_router.urls)),

    # Authentication routes
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]