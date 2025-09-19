from django.urls import path
from . import views, api_views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('login/2fa-complete/', views.two_factor_login_complete_view, name='two_factor_login_complete'),
    path('google/', views.google_login_view, name='google_login'),
    path('refresh/', views.refresh_view, name='refresh'),
    path('me/', views.me_view, name='me'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('health/', views.health_view, name='health'),
    
    # Two-Factor Authentication endpoints
    path('2fa/setup/', views.two_factor_setup_view, name='two_factor_setup'),
    path('2fa/enable/', views.two_factor_enable_view, name='two_factor_enable'),
    path('2fa/verify/', views.two_factor_verify_view, name='two_factor_verify'),
    path('2fa/disable/', views.two_factor_disable_view, name='two_factor_disable'),
    path('2fa/status/', views.two_factor_status_view, name='two_factor_status'),
    
    # Rate Limiting and Security Management endpoints
    path('security/rate-limit-status/', api_views.rate_limit_status_view, name='rate_limit_status'),
    path('security/rate-limit-config/', api_views.rate_limit_config_view, name='rate_limit_config'),
    path('security/dashboard/', api_views.security_dashboard_view, name='security_dashboard'),
    path('security/unblock-ip/', api_views.unblock_ip_view, name='unblock_ip'),
    path('security/block-ip/', api_views.block_ip_view, name='block_ip'),
    path('security/visitor-logs/', api_views.visitor_logs_view, name='visitor_logs'),
]
