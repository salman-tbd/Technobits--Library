"""
Django management command to clear rate limiting data.
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from authentication.rate_limiter import rate_limiter
from authentication.models import VisitorLog, BlockedIP, TwoFactorAttempt


class Command(BaseCommand):
    help = 'Clear rate limiting data from Redis and database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--ip',
            type=str,
            help='Clear rate limits for specific IP address',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Clear rate limits for specific user (email)',
        )
        parser.add_argument(
            '--action',
            type=str,
            default='login',
            help='Action type to clear (login, api, 2fa, etc.)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all rate limiting data',
        )
        parser.add_argument(
            '--expired',
            action='store_true',
            help='Clear only expired blocks and old logs',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Days of data to keep when clearing old logs',
        )
    
    def handle(self, *args, **options):
        if options['all']:
            self.clear_all_data(options['days'])
        elif options['expired']:
            self.clear_expired_data(options['days'])
        elif options['ip'] or options['user']:
            self.clear_specific_limits(
                ip_address=options['ip'],
                user_identifier=options['user'],
                action=options['action']
            )
        else:
            raise CommandError('Please specify --ip, --user, --all, or --expired')
    
    def clear_all_data(self, days_to_keep):
        """Clear all rate limiting data."""
        self.stdout.write(self.style.WARNING('Clearing ALL rate limiting data...'))
        
        # Clear Redis data
        try:
            if rate_limiter.redis_client:
                # Get all rate limit keys
                keys = rate_limiter.redis_client.keys('rate_limit:*')
                if keys:
                    rate_limiter.redis_client.delete(*keys)
                    self.stdout.write(f'Cleared {len(keys)} Redis keys')
                else:
                    self.stdout.write('No Redis keys found')
            else:
                self.stdout.write(self.style.WARNING('Redis not available'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing Redis: {e}'))
        
        # Clear old database records
        self.clear_old_logs(days_to_keep)
        
        # Clear expired IP blocks
        expired_blocks = BlockedIP.objects.filter(
            is_active=True,
            is_permanent=False,
            block_expires_at__lt=timezone.now()
        )
        count = expired_blocks.update(is_active=False)
        self.stdout.write(f'Deactivated {count} expired IP blocks')
        
        self.stdout.write(self.style.SUCCESS('All rate limiting data cleared'))
    
    def clear_expired_data(self, days_to_keep):
        """Clear only expired and old data."""
        self.stdout.write('Clearing expired rate limiting data...')
        
        # Clear old logs
        self.clear_old_logs(days_to_keep)
        
        # Clear expired IP blocks
        expired_blocks = BlockedIP.objects.filter(
            is_active=True,
            is_permanent=False,
            block_expires_at__lt=timezone.now()
        )
        count = expired_blocks.update(is_active=False)
        self.stdout.write(f'Deactivated {count} expired IP blocks')
        
        self.stdout.write(self.style.SUCCESS('Expired data cleared'))
    
    def clear_specific_limits(self, ip_address=None, user_identifier=None, action='login'):
        """Clear rate limits for specific IP or user."""
        if ip_address:
            self.stdout.write(f'Clearing rate limits for IP: {ip_address}')
            rate_limiter.clear_rate_limit(ip_address=ip_address, action=action)
            
            # Also clear from blocked IPs if exists
            try:
                blocked_ip = BlockedIP.objects.get(ip_address=ip_address, is_active=True)
                blocked_ip.is_active = False
                blocked_ip.save()
                self.stdout.write(f'Unblocked IP: {ip_address}')
            except BlockedIP.DoesNotExist:
                pass
        
        if user_identifier:
            self.stdout.write(f'Clearing rate limits for user: {user_identifier}')
            rate_limiter.clear_rate_limit(user_identifier=user_identifier, action=action)
        
        self.stdout.write(self.style.SUCCESS('Specific rate limits cleared'))
    
    def clear_old_logs(self, days_to_keep):
        """Clear old visitor logs and 2FA attempts."""
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Clear old visitor logs
        old_logs = VisitorLog.objects.filter(timestamp__lt=cutoff_date)
        log_count = old_logs.count()
        old_logs.delete()
        self.stdout.write(f'Cleared {log_count} old visitor logs')
        
        # Clear old 2FA attempts
        old_attempts = TwoFactorAttempt.objects.filter(created_at__lt=cutoff_date)
        attempt_count = old_attempts.count()
        old_attempts.delete()
        self.stdout.write(f'Cleared {attempt_count} old 2FA attempts')
