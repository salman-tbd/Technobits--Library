"""
Django management command to show rate limiting statistics.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from authentication.models import VisitorLog, BlockedIP, TwoFactorAttempt, RateLimitConfig
from authentication.rate_limiter import rate_limiter


class Command(BaseCommand):
    help = 'Show rate limiting statistics and status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to analyze (default: 7)',
        )
        parser.add_argument(
            '--ip',
            type=str,
            help='Show detailed stats for specific IP address',
        )
        parser.add_argument(
            '--redis',
            action='store_true',
            help='Show Redis connection status and keys',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        specific_ip = options['ip']
        
        self.stdout.write(self.style.SUCCESS(f'=== Rate Limiting Statistics (Last {days} days) ===\n'))
        
        # Show Redis status
        if options['redis']:
            self.show_redis_status()
        
        # Show configuration
        self.show_configuration()
        
        # Show general statistics
        self.show_general_stats(days)
        
        # Show blocked IPs
        self.show_blocked_ips()
        
        # Show specific IP details if requested
        if specific_ip:
            self.show_ip_details(specific_ip, days)
        
        # Show top suspicious activities
        self.show_suspicious_activities(days)
    
    def show_redis_status(self):
        """Show Redis connection and key status."""
        self.stdout.write(self.style.WARNING('--- Redis Status ---'))
        
        if rate_limiter.redis_client:
            try:
                # Test Redis connection
                rate_limiter.redis_client.ping()
                self.stdout.write(self.style.SUCCESS('✓ Redis connection: OK'))
                
                # Count rate limit keys
                keys = rate_limiter.redis_client.keys('rate_limit:*')
                self.stdout.write(f'Rate limit keys: {len(keys)}')
                
                # Show key breakdown
                key_types = {}
                for key in keys:
                    parts = key.split(':')
                    if len(parts) >= 3:
                        key_type = f"{parts[1]}:{parts[2]}"  # action:type
                        key_types[key_type] = key_types.get(key_type, 0) + 1
                
                for key_type, count in key_types.items():
                    self.stdout.write(f'  {key_type}: {count} keys')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Redis error: {e}'))
        else:
            self.stdout.write(self.style.ERROR('✗ Redis connection: Not available'))
        
        self.stdout.write('')
    
    def show_configuration(self):
        """Show current rate limiting configuration."""
        self.stdout.write(self.style.WARNING('--- Configuration ---'))
        
        try:
            config = RateLimitConfig.objects.filter(is_active=True).first()
            if config:
                self.stdout.write(f'Active config: {config.name}')
                self.stdout.write(f'Login limits (IP): {config.login_ip_limit_per_minute}/min, {config.login_ip_limit_per_hour}/hour')
                self.stdout.write(f'Login limits (User): {config.login_user_limit_per_minute}/min, {config.login_user_limit_per_hour}/hour')
                self.stdout.write(f'API limits (IP): {config.api_ip_limit_per_minute}/min, {config.api_ip_limit_per_hour}/hour')
                self.stdout.write(f'Lockout durations: IP={config.ip_lockout_duration}s, User={config.user_lockout_duration}s')
            else:
                self.stdout.write(self.style.WARNING('No active configuration found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading configuration: {e}'))
        
        self.stdout.write('')
    
    def show_general_stats(self, days):
        """Show general statistics."""
        self.stdout.write(self.style.WARNING('--- General Statistics ---'))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Total requests
        total_requests = VisitorLog.objects.filter(timestamp__gte=cutoff_date).count()
        self.stdout.write(f'Total requests: {total_requests:,}')
        
        # Suspicious requests
        suspicious_requests = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            is_suspicious=True
        ).count()
        self.stdout.write(f'Suspicious requests: {suspicious_requests:,} ({self.percentage(suspicious_requests, total_requests)})')
        
        # Failed authentications
        failed_auth = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            request_path__icontains='/auth/',
            status_code__gte=400
        ).count()
        self.stdout.write(f'Failed auth attempts: {failed_auth:,}')
        
        # Unique IPs
        unique_ips = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date
        ).values('ip_address').distinct().count()
        self.stdout.write(f'Unique IP addresses: {unique_ips:,}')
        
        # 2FA attempts
        totp_attempts = TwoFactorAttempt.objects.filter(created_at__gte=cutoff_date).count()
        successful_2fa = TwoFactorAttempt.objects.filter(
            created_at__gte=cutoff_date,
            success=True
        ).count()
        self.stdout.write(f'2FA attempts: {totp_attempts:,} (Success: {successful_2fa:,})')
        
        self.stdout.write('')
    
    def show_blocked_ips(self):
        """Show currently blocked IPs."""
        self.stdout.write(self.style.WARNING('--- Blocked IPs ---'))
        
        # Active blocks
        active_blocks = BlockedIP.objects.filter(is_active=True).order_by('-blocked_at')
        self.stdout.write(f'Currently blocked IPs: {active_blocks.count()}')
        
        for block in active_blocks[:10]:  # Show top 10
            status = "Permanent" if block.is_permanent else f"Until {block.block_expires_at}"
            self.stdout.write(f'  {block.ip_address}: {block.reason} ({status})')
        
        if active_blocks.count() > 10:
            self.stdout.write(f'  ... and {active_blocks.count() - 10} more')
        
        # Recent blocks (last 24 hours)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_blocks = BlockedIP.objects.filter(blocked_at__gte=recent_cutoff).count()
        self.stdout.write(f'New blocks (24h): {recent_blocks}')
        
        self.stdout.write('')
    
    def show_ip_details(self, ip_address, days):
        """Show detailed statistics for specific IP."""
        self.stdout.write(self.style.WARNING(f'--- Details for IP: {ip_address} ---'))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Request statistics
        ip_logs = VisitorLog.objects.filter(
            ip_address=ip_address,
            timestamp__gte=cutoff_date
        )
        
        total_requests = ip_logs.count()
        suspicious_requests = ip_logs.filter(is_suspicious=True).count()
        auth_requests = ip_logs.filter(request_path__icontains='/auth/').count()
        
        self.stdout.write(f'Total requests: {total_requests}')
        self.stdout.write(f'Suspicious requests: {suspicious_requests}')
        self.stdout.write(f'Auth requests: {auth_requests}')
        
        # Most accessed paths
        paths = ip_logs.values('request_path').annotate(
            count=Count('request_path')
        ).order_by('-count')[:5]
        
        self.stdout.write('Top paths:')
        for path in paths:
            self.stdout.write(f'  {path["request_path"]}: {path["count"]} requests')
        
        # Block status
        try:
            blocked_ip = BlockedIP.objects.get(ip_address=ip_address)
            status = "Active" if blocked_ip.is_active else "Inactive"
            self.stdout.write(f'Block status: {status}')
            self.stdout.write(f'Block reason: {blocked_ip.reason}')
            self.stdout.write(f'Attempt count: {blocked_ip.attempt_count}')
        except BlockedIP.DoesNotExist:
            self.stdout.write('Block status: Not blocked')
        
        self.stdout.write('')
    
    def show_suspicious_activities(self, days):
        """Show top suspicious activities."""
        self.stdout.write(self.style.WARNING('--- Top Suspicious Activities ---'))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Top suspicious IPs
        suspicious_ips = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            is_suspicious=True
        ).values('ip_address').annotate(
            count=Count('ip_address')
        ).order_by('-count')[:10]
        
        self.stdout.write('Most suspicious IPs:')
        for ip_data in suspicious_ips:
            self.stdout.write(f'  {ip_data["ip_address"]}: {ip_data["count"]} suspicious requests')
        
        # Failed login attempts by IP
        failed_logins = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            request_path__icontains='/auth/login',
            status_code__gte=400
        ).values('ip_address').annotate(
            count=Count('ip_address')
        ).order_by('-count')[:5]
        
        self.stdout.write('\nMost failed login attempts:')
        for login_data in failed_logins:
            self.stdout.write(f'  {login_data["ip_address"]}: {login_data["count"]} failed attempts')
        
        self.stdout.write('')
    
    def percentage(self, part, total):
        """Calculate percentage safely."""
        if total == 0:
            return "0%"
        return f"{(part / total * 100):.1f}%"
