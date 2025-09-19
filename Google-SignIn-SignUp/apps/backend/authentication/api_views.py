"""
API views for rate limiting management and monitoring.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import logging

from .models import RateLimitConfig, VisitorLog, BlockedIP, IPBlockRule
from .rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rate_limit_status_view(request):
    """Get current rate limit status for the requesting user/IP."""
    try:
        ip_address = rate_limiter.get_client_ip(request)
        user_identifier = request.user.email if request.user.is_authenticated else None
        
        # Get status for different actions
        actions = ['login', 'api', '2fa', 'register']
        status_data = {}
        
        for action in actions:
            action_status = rate_limiter.get_rate_limit_status(
                request=request,
                action=action,
                user_identifier=user_identifier
            )
            status_data[action] = action_status
        
        # Check if IP is blocked
        is_blocked = rate_limiter._is_ip_blocked(ip_address)
        
        response_data = {
            'ip_address': ip_address,
            'user_email': user_identifier,
            'is_blocked': is_blocked,
            'rate_limits': status_data,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return Response({
            'error': 'Failed to get rate limit status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def rate_limit_config_view(request):
    """Get current rate limiting configuration."""
    try:
        config = RateLimitConfig.objects.filter(is_active=True).first()
        
        if not config:
            return Response({
                'error': 'No active rate limit configuration found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        config_data = {
            'name': config.name,
            'is_active': config.is_active,
            'login_limits': {
                'ip_per_minute': config.login_ip_limit_per_minute,
                'ip_per_hour': config.login_ip_limit_per_hour,
                'ip_per_day': config.login_ip_limit_per_day,
                'user_per_minute': config.login_user_limit_per_minute,
                'user_per_hour': config.login_user_limit_per_hour,
                'user_per_day': config.login_user_limit_per_day,
            },
            'api_limits': {
                'ip_per_minute': config.api_ip_limit_per_minute,
                'ip_per_hour': config.api_ip_limit_per_hour,
                'user_per_minute': config.api_user_limit_per_minute,
                'user_per_hour': config.api_user_limit_per_hour,
            },
            'lockout_settings': {
                'ip_lockout_duration': config.ip_lockout_duration,
                'user_lockout_duration': config.user_lockout_duration,
                'enable_progressive_delays': config.enable_progressive_delays,
                'suspicious_activity_threshold': config.suspicious_activity_threshold,
            },
            'created_at': config.created_at.isoformat(),
            'updated_at': config.updated_at.isoformat(),
        }
        
        return Response(config_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting rate limit config: {e}")
        return Response({
            'error': 'Failed to get rate limit configuration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def security_dashboard_view(request):
    """Get security dashboard data."""
    try:
        # Get time range parameter
        days = int(request.query_params.get('days', 7))
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # General statistics
        total_requests = VisitorLog.objects.filter(timestamp__gte=cutoff_date).count()
        suspicious_requests = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            is_suspicious=True
        ).count()
        
        unique_ips = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date
        ).values('ip_address').distinct().count()
        
        # Authentication statistics
        auth_requests = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            request_path__icontains='/auth/'
        ).count()
        
        failed_auth = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            request_path__icontains='/auth/',
            status_code__gte=400
        ).count()
        
        # Blocked IPs
        active_blocks = BlockedIP.objects.filter(is_active=True).count()
        recent_blocks = BlockedIP.objects.filter(
            blocked_at__gte=cutoff_date
        ).count()
        
        # Top suspicious IPs
        top_suspicious_ips = VisitorLog.objects.filter(
            timestamp__gte=cutoff_date,
            is_suspicious=True
        ).values('ip_address').annotate(
            count=Count('ip_address')
        ).order_by('-count')[:10]
        
        # Recent blocked IPs
        recent_blocked_ips = BlockedIP.objects.filter(
            is_active=True
        ).order_by('-blocked_at')[:10].values(
            'ip_address', 'reason', 'blocked_at', 'attempt_count'
        )
        
        # Request trends (daily breakdown)
        daily_stats = []
        for i in range(days):
            day_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_requests = VisitorLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end
            ).count()
            
            day_suspicious = VisitorLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end,
                is_suspicious=True
            ).count()
            
            daily_stats.append({
                'date': day_start.date().isoformat(),
                'total_requests': day_requests,
                'suspicious_requests': day_suspicious,
            })
        
        dashboard_data = {
            'time_range_days': days,
            'statistics': {
                'total_requests': total_requests,
                'suspicious_requests': suspicious_requests,
                'unique_ips': unique_ips,
                'auth_requests': auth_requests,
                'failed_auth': failed_auth,
                'active_blocks': active_blocks,
                'recent_blocks': recent_blocks,
            },
            'top_suspicious_ips': list(top_suspicious_ips),
            'recent_blocked_ips': list(recent_blocked_ips),
            'daily_trends': daily_stats,
            'generated_at': timezone.now().isoformat(),
        }
        
        return Response(dashboard_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error generating security dashboard: {e}")
        return Response({
            'error': 'Failed to generate security dashboard'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def unblock_ip_view(request):
    """Unblock a specific IP address."""
    try:
        ip_address = request.data.get('ip_address')
        if not ip_address:
            return Response({
                'error': 'IP address is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update blocked IP record
        blocked_ips = BlockedIP.objects.filter(
            ip_address=ip_address,
            is_active=True
        )
        
        if not blocked_ips.exists():
            return Response({
                'error': f'No active block found for IP {ip_address}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        count = blocked_ips.update(is_active=False)
        
        # Clear Redis rate limiting data
        rate_limiter.clear_rate_limit(ip_address=ip_address)
        
        logger.info(f"Admin {request.user.email} unblocked IP {ip_address}")
        
        return Response({
            'message': f'Successfully unblocked IP {ip_address}',
            'unblocked_count': count
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error unblocking IP: {e}")
        return Response({
            'error': 'Failed to unblock IP address'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def block_ip_view(request):
    """Manually block an IP address."""
    try:
        ip_address = request.data.get('ip_address')
        reason = request.data.get('reason', 'Manually blocked by admin')
        duration_hours = int(request.data.get('duration_hours', 24))
        is_permanent = request.data.get('is_permanent', False)
        
        if not ip_address:
            return Response({
                'error': 'IP address is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update blocked IP record
        blocked_ip, created = BlockedIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'is_permanent': is_permanent,
                'blocked_by_admin': True,
                'is_active': True,
                'attempt_count': 0,
            }
        )
        
        if not created:
            # Update existing record
            blocked_ip.reason = reason
            blocked_ip.is_permanent = is_permanent
            blocked_ip.blocked_by_admin = True
            blocked_ip.is_active = True
            blocked_ip.blocked_at = timezone.now()
        
        # Set expiration if not permanent
        if not is_permanent:
            blocked_ip.block_expires_at = timezone.now() + timedelta(hours=duration_hours)
        
        blocked_ip.admin_notes = f"Manually blocked by {request.user.email}"
        blocked_ip.save()
        
        logger.warning(f"Admin {request.user.email} manually blocked IP {ip_address}: {reason}")
        
        return Response({
            'message': f'Successfully blocked IP {ip_address}',
            'block_details': {
                'ip_address': ip_address,
                'reason': reason,
                'is_permanent': is_permanent,
                'expires_at': blocked_ip.block_expires_at.isoformat() if blocked_ip.block_expires_at else None,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error blocking IP: {e}")
        return Response({
            'error': 'Failed to block IP address'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def visitor_logs_view(request):
    """Get recent visitor logs with filtering options."""
    try:
        # Query parameters
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 50)), 100)  # Max 100 records
        ip_filter = request.query_params.get('ip')
        path_filter = request.query_params.get('path')
        suspicious_only = request.query_params.get('suspicious_only', '').lower() == 'true'
        days = int(request.query_params.get('days', 1))
        
        # Build query
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = VisitorLog.objects.filter(timestamp__gte=cutoff_date)
        
        if ip_filter:
            queryset = queryset.filter(ip_address__icontains=ip_filter)
        
        if path_filter:
            queryset = queryset.filter(request_path__icontains=path_filter)
        
        if suspicious_only:
            queryset = queryset.filter(is_suspicious=True)
        
        # Pagination
        total_count = queryset.count()
        offset = (page - 1) * page_size
        logs = queryset.order_by('-timestamp')[offset:offset + page_size]
        
        # Serialize logs
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'ip_address': log.ip_address,
                'request_path': log.request_path,
                'request_method': log.request_method,
                'user_email': log.user.email if log.user else None,
                'is_authenticated': log.is_authenticated,
                'username_attempted': log.username_attempted,
                'is_suspicious': log.is_suspicious,
                'status_code': log.status_code,
                'timestamp': log.timestamp.isoformat(),
                'user_agent': log.user_agent[:100] if log.user_agent else None,  # Truncate for display
            })
        
        return Response({
            'logs': logs_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
            },
            'filters': {
                'ip': ip_filter,
                'path': path_filter,
                'suspicious_only': suspicious_only,
                'days': days,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting visitor logs: {e}")
        return Response({
            'error': 'Failed to get visitor logs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
