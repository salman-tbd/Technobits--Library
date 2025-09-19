"""
URL configuration for stripe_gateway project.
Simple URL routing for Stripe payment processing.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('payments.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = 'Stripe Payment Gateway Admin'
admin.site.site_title = 'Stripe Gateway'
admin.site.index_title = 'Payment Gateway Administration'

