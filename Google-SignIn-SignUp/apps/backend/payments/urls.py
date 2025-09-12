"""
Payment URLs Configuration
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Google Pay endpoints
    path('google-pay/process/', views.GooglePayProcessView.as_view(), name='google_pay_process'),
    
    # PayPal endpoints
    path('paypal/create-order/', views.PayPalCreateOrderView.as_view(), name='paypal_create_order'),
    path('paypal/capture-order/', views.PayPalCaptureOrderView.as_view(), name='paypal_capture_order'),
    path('paypal/webhook/', views.PayPalWebhookView.as_view(), name='paypal_webhook'),
    
    # Transaction management
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<str:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Analytics
    path('analytics/', views.PaymentAnalyticsView.as_view(), name='payment_analytics'),
]
