"""
Rate limiting middleware for Django authentication system.
Provides comprehensive request protection and logging.
"""
import logging
import time
import re
from typing import List, Dict
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware for rate limiting and request monitoring.
    Inspired by digiassistants.com but enhanced with Redis.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
        self.rate_limiter = rate_limiter
        
        # Paths that should be excluded from rate limiting
        self.excluded_paths = [
            '/admin/jsi18n/',
            '/favicon.ico',
            '/static/',
            '/media/',
            '/health/',
        ]
        
        # Paths that require stricter rate limiting
        self.strict_paths = [
            '/auth/login/',
            '/auth/register/',
            '/auth/forgot-password/',
            '/auth/reset-password/',
            '/auth/2fa/',
        ]
        
        # Paths that should be monitored for suspicious activity
        self.monitored_paths = [
            '/auth/',
            '/admin/',
        ]
    
    def process_request(self, request):
        """Process incoming request for rate limiting."""
        # Debug logging
        logger.info(f"🔍 RateLimitMiddleware processing: {request.path}")
        
        # Skip rate limiting for excluded paths
        if self._is_excluded_path(request.path):
            logger.info(f"📋 Excluded path: {request.path}")
            return None
        
        # Determine action type based on path
        action = self._get_action_type(request.path, request.method)
        
        # Get user identifier if available
        user_identifier = self._get_user_identifier(request)
        
        # Check rate limits
        is_limited, rate_limit_info = self.rate_limiter.check_rate_limit(
            request=request,
            action=action,
            user_identifier=user_identifier
        )
        
        # Handle rate limiting
        if is_limited:
            return self._handle_rate_limit_exceeded(request, rate_limit_info)
        
        # Store rate limit info in request for later use
        request.rate_limit_info = rate_limit_info
        
        return None
    
    def process_response(self, request, response):
        """Process response and record request data."""
        # Debug logging
        logger.info(f"🔍 RateLimitMiddleware response: {request.path} -> {response.status_code}")
        
        # Skip processing for excluded paths
        if self._is_excluded_path(request.path):
            logger.info(f"📋 Excluded from response processing: {request.path}")
            return response
        
        # Determine if request was successful
        success = 200 <= response.status_code < 400
        
        # Record the request
        action = self._get_action_type(request.path, request.method)
        user_identifier = self._get_user_identifier(request)
        
        self.rate_limiter.record_request(
            request=request,
            action=action,
            user_identifier=user_identifier,
            success=success
        )
        
        # Add rate limit headers to response
        if hasattr(request, 'rate_limit_info'):
            self._add_rate_limit_headers(response, request.rate_limit_info)
        
        # Check for suspicious activity
        if not success and self._is_monitored_path(request.path):
            self._handle_suspicious_activity(request, response)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path should be excluded from rate limiting."""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def _is_strict_path(self, path: str) -> bool:
        """Check if path requires strict rate limiting."""
        for strict in self.strict_paths:
            if path.startswith(strict):
                return True
        return False
    
    def _is_monitored_path(self, path: str) -> bool:
        """Check if path should be monitored for suspicious activity."""
        for monitored in self.monitored_paths:
            if path.startswith(monitored):
                return True
        return False
    
    def _get_action_type(self, path: str, method: str) -> str:
        """Determine the action type based on request path and method."""
        # Login-related actions
        if '/auth/login/' in path or '/auth/google/' in path:
            return 'login'
        elif '/auth/register/' in path:
            return 'register'
        elif '/auth/forgot-password/' in path or '/auth/reset-password/' in path:
            return 'password_reset'
        elif '/auth/2fa/' in path:
            return '2fa'
        elif '/auth/' in path:
            return 'auth'
        elif '/admin/' in path:
            return 'admin'
        else:
            return 'api'
    
    def _get_user_identifier(self, request) -> str:
        """Extract user identifier from request."""
        # If user is authenticated, use their email/username
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user.email or request.user.username
        
        # For login attempts, try to extract email from POST data
        if request.method == 'POST':
            # Common field names for user identification
            for field in ['email', 'username', 'user', 'login']:
                if field in request.POST:
                    return request.POST[field]
            
            # Try JSON data
            if hasattr(request, 'data') and isinstance(request.data, dict):
                for field in ['email', 'username', 'user', 'login']:
                    if field in request.data:
                        return request.data[field]
        
        return None
    
    def _handle_rate_limit_exceeded(self, request, rate_limit_info: Dict) -> JsonResponse:
        """Handle rate limit exceeded scenarios."""
        retry_after = rate_limit_info.get('retry_after', 60)
        
        # Determine the reason for rate limiting
        reasons = []
        if rate_limit_info.get('ip_limited'):
            reasons.append("Too many requests from your IP address")
        if rate_limit_info.get('user_limited'):
            reasons.append("Too many requests for this account")
        if rate_limit_info.get('ip_blocked'):
            reasons.append("Your IP address has been temporarily blocked")
        
        reason = ". ".join(reasons) if reasons else "Rate limit exceeded"
        
        # Log the rate limit event
        logger.warning(
            f"Rate limit exceeded: {self.rate_limiter.get_client_ip(request)} "
            f"- {request.path} - {reason}"
        )
        
        # Return rate limit response
        response_data = {
            'error': 'Rate limit exceeded',
            'message': f"{reason}. Please try again later.",
            'retry_after': retry_after,
            'detail': rate_limit_info
        }
        
        response = JsonResponse(response_data, status=429)
        response['Retry-After'] = str(retry_after)
        response['X-RateLimit-Exceeded'] = 'true'
        
        return response
    
    def _add_rate_limit_headers(self, response, rate_limit_info: Dict):
        """Add rate limit headers to response."""
        try:
            ip_info = rate_limit_info.get('ip_info', {})
            user_info = rate_limit_info.get('user_info', {})
            
            # Add IP-based headers
            if 'minute_limit' in ip_info:
                response['X-RateLimit-Limit'] = str(ip_info['minute_limit'])
                response['X-RateLimit-Remaining'] = str(ip_info['minute_remaining'])
            
            # Add retry-after header if limited
            if rate_limit_info.get('retry_after'):
                response['Retry-After'] = str(rate_limit_info['retry_after'])
        
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")
    
    def _handle_suspicious_activity(self, request, response):
        """Handle suspicious activity detection."""
        try:
            from .models import BlockedIP, IPBlockRule
            
            ip_address = self.rate_limiter.get_client_ip(request)
            
            # Check for existing block rules
            matching_rules = IPBlockRule.objects.filter(
                is_active=True,
                request_path_pattern__isnull=False
            )
            
            for rule in matching_rules:
                if self._path_matches_pattern(request.path, rule.request_path_pattern):
                    self._apply_block_rule(ip_address, rule, request)
        
        except Exception as e:
            logger.error(f"Error handling suspicious activity: {e}")
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches the given pattern (supports regex)."""
        try:
            return bool(re.search(pattern, path))
        except re.error:
            # If regex is invalid, fall back to simple string matching
            return pattern in path
    
    def _apply_block_rule(self, ip_address: str, rule, request):
        """Apply block rule to IP address."""
        try:
            from .models import BlockedIP
            from django.utils import timezone
            
            # Get or create blocked IP record
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'rule': rule,
                    'reason': f"Triggered rule: {rule.name}",
                    'is_permanent': rule.is_permanent_block,
                    'attempt_count': 0,
                }
            )
            
            # Update attempt count
            blocked_ip.attempt_count += 1
            blocked_ip.last_attempt_at = timezone.now()
            
            # Set block expiration if not permanent
            if not blocked_ip.is_permanent and rule.block_duration:
                blocked_ip.block_expires_at = timezone.now() + timezone.timedelta(
                    seconds=rule.block_duration
                )
            
            # Activate block if threshold exceeded
            if blocked_ip.attempt_count >= rule.max_attempts:
                blocked_ip.is_active = True
                
                logger.warning(
                    f"IP {ip_address} blocked due to rule '{rule.name}' "
                    f"({blocked_ip.attempt_count} attempts)"
                )
            
            blocked_ip.save()
        
        except Exception as e:
            logger.error(f"Error applying block rule: {e}")


class IPBlockMiddleware(MiddlewareMixin):
    """
    Simple middleware to check for blocked IPs.
    This runs before RateLimitMiddleware for faster blocking.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Check if IP is blocked before processing request."""
        try:
            from .models import BlockedIP
            from ipware import get_client_ip
            
            ip_address, _ = get_client_ip(request)
            if not ip_address:
                return None
            
            # Check if IP is blocked
            blocked_ip = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).first()
            
            if blocked_ip and blocked_ip.is_blocked():
                logger.warning(f"Blocked IP {ip_address} attempted access to {request.path}")
                
                return JsonResponse({
                    'error': 'Access denied',
                    'message': 'Your IP address has been blocked due to suspicious activity.',
                    'blocked_at': blocked_ip.blocked_at.isoformat(),
                    'reason': blocked_ip.reason,
                }, status=403)
        
        except Exception as e:
            logger.error(f"Error in IP block middleware: {e}")
        
        return None
