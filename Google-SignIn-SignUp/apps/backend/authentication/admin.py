from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    UserTwoFactor, TwoFactorBackupCode, TwoFactorAttempt,
    RateLimitConfig, VisitorLog, IPBlockRule, BlockedIP
)


@admin.register(UserTwoFactor)
class UserTwoFactorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_enabled', 'backup_tokens_count', 'created_at', 'last_used_at')
    list_filter = ('is_enabled', 'created_at', 'last_used_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('secret_key_encrypted', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Two-Factor Settings', {
            'fields': ('is_enabled', 'backup_tokens_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TwoFactorBackupCode)
class TwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = ('user_two_factor', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user_two_factor__user__email',)
    readonly_fields = ('code_hash', 'created_at', 'used_at')


@admin.register(TwoFactorAttempt)
class TwoFactorAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'attempt_type', 'success', 'created_at')
    list_filter = ('success', 'attempt_type', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(RateLimitConfig)
class RateLimitConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'login_ip_limit_per_minute', 'login_user_limit_per_minute', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Configuration', {
            'fields': ('name', 'is_active')
        }),
        ('Login Rate Limits', {
            'fields': (
                'login_ip_limit_per_minute', 'login_ip_limit_per_hour', 'login_ip_limit_per_day',
                'login_user_limit_per_minute', 'login_user_limit_per_hour', 'login_user_limit_per_day'
            )
        }),
        ('API Rate Limits', {
            'fields': (
                'api_ip_limit_per_minute', 'api_ip_limit_per_hour',
                'api_user_limit_per_minute', 'api_user_limit_per_hour'
            )
        }),
        ('Security Settings', {
            'fields': (
                'ip_lockout_duration', 'user_lockout_duration',
                'enable_progressive_delays', 'suspicious_activity_threshold'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'request_path', 'request_method', 'is_authenticated', 'is_suspicious', 'timestamp')
    list_filter = ('is_authenticated', 'is_suspicious', 'request_method', 'timestamp')
    search_fields = ('ip_address', 'request_path', 'username_attempted', 'user__email')
    readonly_fields = ('timestamp', 'unix_timestamp')
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').order_by('-timestamp')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('ip_address', 'request_path', 'request_method', 'user_agent')
        }),
        ('Authentication', {
            'fields': ('user', 'is_authenticated', 'username_attempted')
        }),
        ('Session & Security', {
            'fields': ('session_key', 'is_suspicious', 'status_code')
        }),
        ('Location', {
            'fields': ('country_code', 'city'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'unix_timestamp'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IPBlockRule)
class IPBlockRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'max_attempts', 'time_window', 'block_duration', 'is_permanent_block')
    list_filter = ('is_active', 'is_permanent_block', 'send_alert')
    search_fields = ('name', 'description', 'request_path_pattern')
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Trigger Conditions', {
            'fields': ('request_path_pattern', 'max_attempts', 'time_window')
        }),
        ('Block Settings', {
            'fields': ('block_duration', 'is_permanent_block')
        }),
        ('Notifications', {
            'fields': ('send_alert', 'alert_email')
        }),
    )


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'blocked_at', 'block_status', 'attempt_count', 'blocked_by_admin')
    list_filter = ('is_active', 'is_permanent', 'blocked_by_admin', 'blocked_at')
    search_fields = ('ip_address', 'reason', 'admin_notes')
    readonly_fields = ('blocked_at', 'last_attempt_at')
    actions = ['unblock_ips', 'make_permanent', 'extend_block']
    
    def block_status(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: green;">Inactive</span>')
        elif obj.is_permanent:
            return format_html('<span style="color: red;">Permanent</span>')
        elif obj.block_expires_at and timezone.now() > obj.block_expires_at:
            return format_html('<span style="color: orange;">Expired</span>')
        else:
            return format_html('<span style="color: red;">Active</span>')
    block_status.short_description = 'Status'
    
    def unblock_ips(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} IPs unblocked successfully.')
    unblock_ips.short_description = 'Unblock selected IPs'
    
    def make_permanent(self, request, queryset):
        count = queryset.update(is_permanent=True, is_active=True)
        self.message_user(request, f'{count} IPs permanently blocked.')
    make_permanent.short_description = 'Make block permanent'
    
    def extend_block(self, request, queryset):
        from datetime import timedelta
        new_expiry = timezone.now() + timedelta(hours=24)
        count = queryset.update(block_expires_at=new_expiry, is_active=True)
        self.message_user(request, f'{count} IP blocks extended by 24 hours.')
    extend_block.short_description = 'Extend block by 24 hours'
    
    fieldsets = (
        ('IP Information', {
            'fields': ('ip_address', 'rule')
        }),
        ('Block Details', {
            'fields': ('reason', 'blocked_at', 'block_expires_at', 'is_permanent', 'is_active')
        }),
        ('Statistics', {
            'fields': ('attempt_count', 'last_attempt_at')
        }),
        ('Admin Actions', {
            'fields': ('blocked_by_admin', 'admin_notes')
        }),
    )


# Custom admin site configuration
admin.site.site_header = "Authentication Security Admin"
admin.site.site_title = "Auth Security"
admin.site.index_title = "Security & Rate Limiting Administration"
