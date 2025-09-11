"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint with basic information."""
    return JsonResponse({
        'message': 'Google Sign-In/Sign-Up Backend API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/auth/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('', api_root, name='api_root'),
]
