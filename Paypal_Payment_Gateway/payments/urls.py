"""
PayPal Payment URLs
"""
from django.urls import path
from .views import (
    CreateOrderView,
    CaptureOrderView,
    PayPalWebhookView,
    TransactionStatusView
)

app_name = 'payments'

urlpatterns = [
    # PayPal API endpoints
    path('paypal/create-order/', CreateOrderView.as_view(), name='create_order'),
    path('paypal/capture-order/', CaptureOrderView.as_view(), name='capture_order'),
    path('paypal/webhook/', PayPalWebhookView.as_view(), name='webhook'),
    path('paypal/transaction-status/<str:order_id>/', TransactionStatusView.as_view(), name='transaction_status'),
]
