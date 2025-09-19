"""
Admin configuration for payments app.
"""

from django.contrib import admin
from .models import StripeTransaction


@admin.register(StripeTransaction)
class StripeTransactionAdmin(admin.ModelAdmin):
    """
    Admin for StripeTransaction model.
    """
    list_display = [
        'transaction_id', 'amount', 'currency', 'status', 
        'stripe_session_id', 'created_at'
    ]
    list_filter = [
        'status', 'currency', 'created_at'
    ]
    search_fields = [
        'transaction_id', 'stripe_session_id', 'stripe_payment_intent_id', 
        'description'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'transaction_id', 'stripe_session_id', 'stripe_payment_intent_id',
        'created_at', 'updated_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'transaction_id', 'stripe_session_id', 'stripe_payment_intent_id'
            )
        }),
        ('Payment Details', {
            'fields': (
                'amount', 'currency', 'status', 'description'
            )
        }),
        ('Stripe Response', {
            'fields': ('stripe_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding transactions through admin."""
        return False


# Customize admin site headers
admin.site.site_header = 'Stripe Payment Gateway Administration'
admin.site.site_title = 'Payment Gateway Admin'
admin.site.index_title = 'Payment Management'

