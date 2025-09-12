"""
Payment Admin Interface
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import PaymentTransaction, PaymentWebhook, PaymentMethod


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id_short',
        'user_email',
        'provider',
        'amount_display',
        'status_badge',
        'created_at',
        'completed_at'
    ]
    list_filter = [
        'provider',
        'status',
        'currency',
        'created_at',
        'completed_at'
    ]
    search_fields = [
        'transaction_id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'provider_transaction_id',
        'provider_order_id',
        'provider_payment_id'
    ]
    readonly_fields = [
        'id',
        'transaction_id',
        'provider_response_formatted',
        'created_at',
        'updated_at',
        'completed_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'transaction_id',
                'user',
                'provider',
                'status'
            )
        }),
        ('Transaction Details', {
            'fields': (
                'amount',
                'currency',
                'description'
            )
        }),
        ('Provider Information', {
            'fields': (
                'provider_transaction_id',
                'provider_order_id',
                'provider_payment_id',
                'provider_token',
                'provider_response_formatted'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at'
            )
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def transaction_id_short(self, obj):
        """Display shortened transaction ID"""
        return f"{obj.transaction_id[:20]}..." if len(obj.transaction_id) > 20 else obj.transaction_id
    transaction_id_short.short_description = 'Transaction ID'
    
    def user_email(self, obj):
        """Display user email with link to user admin"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def amount_display(self, obj):
        """Display formatted amount"""
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'created': 'gray',
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def provider_response_formatted(self, obj):
        """Display formatted provider response"""
        if obj.provider_response:
            try:
                formatted = json.dumps(obj.provider_response, indent=2)
                return mark_safe(f'<pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{formatted}</pre>')
            except:
                return str(obj.provider_response)
        return '-'
    provider_response_formatted.short_description = 'Provider Response'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'webhook_id_short',
        'provider',
        'event_type',
        'processed_badge',
        'transaction_link',
        'received_at'
    ]
    list_filter = [
        'provider',
        'event_type',
        'processed',
        'received_at'
    ]
    search_fields = [
        'webhook_id',
        'event_type',
        'transaction__transaction_id'
    ]
    readonly_fields = [
        'webhook_id',
        'provider',
        'event_type',
        'event_data_formatted',
        'received_at',
        'processed_at'
    ]
    fieldsets = (
        ('Webhook Information', {
            'fields': (
                'webhook_id',
                'provider',
                'event_type',
                'transaction'
            )
        }),
        ('Processing Status', {
            'fields': (
                'processed',
                'processed_at',
                'processing_result'
            )
        }),
        ('Event Data', {
            'fields': (
                'event_data_formatted',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'received_at',
            )
        })
    )
    date_hierarchy = 'received_at'
    ordering = ['-received_at']
    
    def webhook_id_short(self, obj):
        """Display shortened webhook ID"""
        return f"{obj.webhook_id[:20]}..." if len(obj.webhook_id) > 20 else obj.webhook_id
    webhook_id_short.short_description = 'Webhook ID'
    
    def processed_badge(self, obj):
        """Display processed status with badge"""
        if obj.processed:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Processed</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Pending</span>'
            )
    processed_badge.short_description = 'Status'
    processed_badge.admin_order_field = 'processed'
    
    def transaction_link(self, obj):
        """Display link to related transaction"""
        if obj.transaction:
            url = reverse('admin:payments_paymenttransaction_change', args=[obj.transaction.pk])
            return format_html('<a href="{}">{}</a>', url, obj.transaction.transaction_id[:20] + '...')
        return '-'
    transaction_link.short_description = 'Transaction'
    
    def event_data_formatted(self, obj):
        """Display formatted event data"""
        if obj.event_data:
            try:
                formatted = json.dumps(obj.event_data, indent=2)
                return mark_safe(f'<pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">{formatted}</pre>')
            except:
                return str(obj.event_data)
        return '-'
    event_data_formatted.short_description = 'Event Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('transaction')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'provider',
        'method_type',
        'last_four_display',
        'brand',
        'is_active_badge',
        'is_default_badge',
        'created_at'
    ]
    list_filter = [
        'provider',
        'method_type',
        'brand',
        'is_active',
        'is_default',
        'created_at'
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'method_type',
        'brand',
        'provider_method_id'
    ]
    readonly_fields = [
        'provider_data_formatted',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'provider',
                'method_type'
            )
        }),
        ('Method Details', {
            'fields': (
                'last_four',
                'brand',
                'provider_method_id'
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'is_default'
            )
        }),
        ('Provider Data', {
            'fields': (
                'provider_data_formatted',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def user_email(self, obj):
        """Display user email with link"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def last_four_display(self, obj):
        """Display last four digits with masking"""
        if obj.last_four:
            return f"**** {obj.last_four}"
        return '-'
    last_four_display.short_description = 'Card Number'
    
    def is_active_badge(self, obj):
        """Display active status badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">Inactive</span>'
            )
    is_active_badge.short_description = 'Active'
    is_active_badge.admin_order_field = 'is_active'
    
    def is_default_badge(self, obj):
        """Display default status badge"""
        if obj.is_default:
            return format_html(
                '<span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">Default</span>'
            )
        return '-'
    is_default_badge.short_description = 'Default'
    is_default_badge.admin_order_field = 'is_default'
    
    def provider_data_formatted(self, obj):
        """Display formatted provider data"""
        if obj.provider_data:
            try:
                formatted = json.dumps(obj.provider_data, indent=2)
                return mark_safe(f'<pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{formatted}</pre>')
            except:
                return str(obj.provider_data)
        return '-'
    provider_data_formatted.short_description = 'Provider Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
