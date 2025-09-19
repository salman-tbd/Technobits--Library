"""
PayPal Payment Admin Configuration
"""
from django.contrib import admin
from .models import PayPalTransaction, PayPalWebhookEvent


@admin.register(PayPalTransaction)
class PayPalTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'paypal_order_id', 
        'amount', 
        'currency', 
        'status', 
        'user', 
        'created_at',
        'completed_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['paypal_order_id', 'paypal_payment_id', 'user__username', 'user__email']
    readonly_fields = ['paypal_order_id', 'paypal_payment_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('PayPal Information', {
            'fields': ('paypal_order_id', 'paypal_payment_id', 'status')
        }),
        ('Transaction Details', {
            'fields': ('amount', 'currency', 'description', 'user')
        }),
        ('PayPal Response', {
            'fields': ('paypal_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PayPalWebhookEvent)
class PayPalWebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_id',
        'event_type', 
        'resource_id',
        'processed',
        'transaction',
        'created_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'resource_id', 'event_type']
    readonly_fields = ['event_id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'resource_id')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'transaction')
        }),
        ('Webhook Data', {
            'fields': ('webhook_data',),
            'classes': ('collapse',)
        }),
    )
