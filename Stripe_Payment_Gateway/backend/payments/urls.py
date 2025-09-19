"""
URLs for payments app.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Intent endpoints
    path('create-payment-intent/', views.create_payment_intent, name='create-payment-intent'),
    
    # Checkout Session endpoints
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('session-status/', views.session_status, name='session-status'),
    
    # Payment management
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('stats/', views.payment_stats, name='payment-stats'),
    
    # Placeholder endpoints (not fully implemented)
    path('<int:payment_id>/refund/', views.create_refund, name='create-refund'),
    path('refunds/', views.RefundListView.as_view(), name='refund-list'),
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('methods/<int:payment_method_id>/', views.delete_payment_method, name='delete-payment-method'),
    path('events/', views.PaymentEventListView.as_view(), name='payment-event-list'),
]

