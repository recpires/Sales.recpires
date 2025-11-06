"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection # Importado para o health_check

def api_root(request):
    """Root endpoint with API information"""
    return JsonResponse({
        'message': 'Sales Management API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'health': '/health/',
            'docs': {
                'products': '/api/products/',
                'orders': '/api/orders/',
                'order_items': '/api/order-items/',
                'stores': '/api/stores/',
                'auth': {
                    'register': '/api/auth/register/',
                    'login': '/api/auth/login/',
                    'logout': '/api/auth/logout/',
                    'refresh': '/api/auth/token/refresh/',
                    'profile': '/api/auth/profile/',
                    'change_password': '/api/auth/change-password/'
                }
            }
        }
    })

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        connection.ensure_connection()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    response_data = {
        'status': 'healthy',
        'database': db_status,
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'method': request.method
    }
    return JsonResponse(response_data)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/', include('sales.urls')),
]

# **Mapeamento de Mídia (Recomendado)**
# Serve arquivos de mídia APENAS em ambiente de DESENVOLVIMENTO (DEBUG=True).
# Em produção, o servidor web ou o S3 deve lidar com isso.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)