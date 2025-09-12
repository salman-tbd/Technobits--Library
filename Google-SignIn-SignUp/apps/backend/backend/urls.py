"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint with basic information."""
    return JsonResponse({
        'message': 'Technobits Directory - Authentication & Payment API',
        'version': '2.0.0',
        'features': [
            'JWT Authentication with Google OAuth',
            'Google Pay Integration', 
            'PayPal Integration',
            'Transaction Management',
            'Payment Analytics'
        ],
        'endpoints': {
            'auth': '/auth/',
            'payments': '/api/payments/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('api/payments/', include('payments.urls')),
    path('', api_root, name='api_root'),
]
