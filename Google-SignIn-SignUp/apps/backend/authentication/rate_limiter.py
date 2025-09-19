"""
Redis-based rate limiting system for authentication endpoints.
Inspired by digiassistants.com but enhanced with Redis for better performance.
"""
import time
import json
import logging
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from ipware import get_client_ip
import redis

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Redis-based rate limiter for per-IP and per-user protection.
    Provides multiple time windows and progressive blocking.
    """
    
    def __init__(self):
        self.redis_client = self._get_redis_connection()
        self.config = self._get_rate_limit_config()
    
    def _get_redis_connection(self):
        """Get Redis connection or return None to use Django cache fallback."""
        try:
            # Try to create Redis connection
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
            client = redis.from_url(redis_url, decode_responses=True)
            # Test the connection
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available, using Django cache fallback: {e}")
            return None
    
    def _get_rate_limit_config(self):
        """Get rate limiting configuration from database."""
        try:
            from .models import RateLimitConfig
            config = RateLimitConfig.objects.filter(is_active=True).first()
            if not config:
                # Create default configuration
                config = RateLimitConfig.objects.create(
                    name="default",
                    login_ip_limit_per_minute=5,
                    login_ip_limit_per_hour=20,
                    login_ip_limit_per_day=100,
                    login_user_limit_per_minute=3,
                    login_user_limit_per_hour=10,
                    login_user_limit_per_day=50,
                    api_ip_limit_per_minute=60,
                    api_ip_limit_per_hour=1000,
                    api_user_limit_per_minute=100,
                    api_user_limit_per_hour=2000,
                )
            return config
        except Exception as e:
            logger.error(f"Failed to get rate limit config: {e}")
            # Return default values
            return type('Config', (), {
                'login_ip_limit_per_minute': 5,
                'login_ip_limit_per_hour': 20,
                'login_ip_limit_per_day': 100,
                'login_user_limit_per_minute': 3,
                'login_user_limit_per_hour': 10,
                'login_user_limit_per_day': 50,
                'api_ip_limit_per_minute': 60,
                'api_ip_limit_per_hour': 1000,
                'api_user_limit_per_minute': 100,
                'api_user_limit_per_hour': 2000,
                'ip_lockout_duration': 900,
                'user_lockout_duration': 600,
                'enable_progressive_delays': True,
                'suspicious_activity_threshold': 3,
            })()
    
    def get_client_ip(self, request):
        """Extract client IP address from request."""
        ip, is_routable = get_client_ip(request)
        return ip or '127.0.0.1'
    
    def get_rate_limit_keys(self, identifier: str, action: str, time_windows: List[str]) -> List[str]:
        """Generate Redis keys for rate limiting."""
        keys = []
        for window in time_windows:
            key = f"rate_limit:{action}:{identifier}:{window}"
            keys.append(key)
        return keys
    
    def check_rate_limit(self, request, action: str = 'login', user_identifier: str = None) -> Tuple[bool, Dict]:
        """
        Check if request should be rate limited.
        
        Args:
            request: Django request object
            action: Action type ('login', 'api', '2fa', etc.)
            user_identifier: User identifier (email, username, or user ID)
        
        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        # Note: We now support Django cache fallback, so continue even without Redis
        if not self.redis_client:
            logger.info("Using Django cache fallback for rate limiting")
        
        ip_address = self.get_client_ip(request)
        current_time = int(time.time())
        
        # Check IP-based rate limiting
        ip_limited, ip_info = self._check_ip_rate_limit(ip_address, action, current_time)
        
        # Check user-based rate limiting (if user identifier provided)
        user_limited, user_info = False, {}
        if user_identifier:
            user_limited, user_info = self._check_user_rate_limit(user_identifier, action, current_time)
        
        # Check if IP is blocked
        ip_blocked = self._is_ip_blocked(ip_address)
        
        is_limited = ip_limited or user_limited or ip_blocked
        
        # Log the attempt
        self._log_attempt(request, action, user_identifier, is_limited, current_time)
        
        rate_limit_info = {
            'ip_limited': ip_limited,
            'user_limited': user_limited,
            'ip_blocked': ip_blocked,
            'ip_info': ip_info,
            'user_info': user_info,
            'retry_after': self._calculate_retry_after(ip_info, user_info),
        }
        
        return is_limited, rate_limit_info
    
    def _check_ip_rate_limit(self, ip_address: str, action: str, current_time: int) -> Tuple[bool, Dict]:
        """Check IP-based rate limiting."""
        # Map certain actions to use login limits
        config_action = action
        if action in ['register', 'password_reset', '2fa']:
            config_action = 'login'
        
        time_windows = {
            'minute': (60, getattr(self.config, f'{config_action}_ip_limit_per_minute', 60)),
            'hour': (3600, getattr(self.config, f'{config_action}_ip_limit_per_hour', 1000)),
            'day': (86400, getattr(self.config, f'{config_action}_ip_limit_per_day', 10000)),
        }
        
        info = {}
        is_limited = False
        
        for window_name, (window_seconds, limit) in time_windows.items():
            window_start = current_time - window_seconds
            key = f"rate_limit:{action}:ip:{ip_address}:{window_name}"
            
            try:
                # Get current count
                count = self._get_request_count(key, window_start, current_time)
                
                info[f'{window_name}_count'] = count
                info[f'{window_name}_limit'] = limit
                info[f'{window_name}_remaining'] = max(0, limit - count)
                
                if count >= limit:
                    is_limited = True
                    info['blocked_window'] = window_name
                    
            except Exception as e:
                logger.error(f"Error checking IP rate limit: {e}")
        
        return is_limited, info
    
    def _check_user_rate_limit(self, user_identifier: str, action: str, current_time: int) -> Tuple[bool, Dict]:
        """Check user-based rate limiting."""
        # Map certain actions to use login limits
        config_action = action
        if action in ['register', 'password_reset', '2fa']:
            config_action = 'login'
        
        time_windows = {
            'minute': (60, getattr(self.config, f'{config_action}_user_limit_per_minute', 100)),
            'hour': (3600, getattr(self.config, f'{config_action}_user_limit_per_hour', 2000)),
            'day': (86400, getattr(self.config, f'{config_action}_user_limit_per_day', 50000)),
        }
        
        info = {}
        is_limited = False
        
        for window_name, (window_seconds, limit) in time_windows.items():
            window_start = current_time - window_seconds
            key = f"rate_limit:{action}:user:{user_identifier}:{window_name}"
            
            try:
                count = self._get_request_count(key, window_start, current_time)
                
                info[f'{window_name}_count'] = count
                info[f'{window_name}_limit'] = limit
                info[f'{window_name}_remaining'] = max(0, limit - count)
                
                if count >= limit:
                    is_limited = True
                    info['blocked_window'] = window_name
                    
            except Exception as e:
                logger.error(f"Error checking user rate limit: {e}")
        
        return is_limited, info
    
    def _get_request_count(self, key: str, window_start: int, current_time: int) -> int:
        """Get request count for a time window."""
        if self.redis_client:
            return self._get_request_count_redis(key, window_start, current_time)
        else:
            return self._get_request_count_cache(key, window_start, current_time)
    
    def _get_request_count_redis(self, key: str, window_start: int, current_time: int) -> int:
        """Get request count using Redis sorted sets."""
        try:
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current entries
            count = self.redis_client.zcard(key)
            
            return count
        except Exception as e:
            logger.error(f"Error getting request count from Redis: {e}")
            return 0
    
    def _get_request_count_cache(self, key: str, window_start: int, current_time: int) -> int:
        """Get request count using Django cache (fallback)."""
        try:
            # Get list of timestamps from cache
            timestamps = cache.get(key, [])
            
            # Filter out old entries
            valid_timestamps = [ts for ts in timestamps if ts >= window_start]
            
            # Update cache with filtered timestamps
            if len(valid_timestamps) != len(timestamps):
                cache.set(key, valid_timestamps, 300)  # 5 minute timeout
            
            return len(valid_timestamps)
        except Exception as e:
            logger.error(f"Error getting request count from cache: {e}")
            return 0
    
    def record_request(self, request, action: str = 'api', user_identifier: str = None, success: bool = True):
        """
        Record a request for rate limiting tracking.
        
        Args:
            request: Django request object
            action: Action type
            user_identifier: User identifier
            success: Whether the request was successful
        """
        ip_address = self.get_client_ip(request)
        current_time = int(time.time())
        
        # Record IP-based request
        self._record_ip_request(ip_address, action, current_time, success)
        
        # Record user-based request (if available)
        if user_identifier:
            self._record_user_request(user_identifier, action, current_time, success)
    
    def _record_ip_request(self, ip_address: str, action: str, current_time: int, success: bool):
        """Record IP-based request."""
        if self.redis_client:
            self._record_ip_request_redis(ip_address, action, current_time, success)
        else:
            self._record_ip_request_cache(ip_address, action, current_time, success)
    
    def _record_ip_request_redis(self, ip_address: str, action: str, current_time: int, success: bool):
        """Record IP-based request using Redis."""
        time_windows = ['minute', 'hour', 'day']
        
        for window in time_windows:
            key = f"rate_limit:{action}:ip:{ip_address}:{window}"
            
            try:
                # Add current request with timestamp as score
                self.redis_client.zadd(key, {f"{current_time}:{success}": current_time})
                
                # Set expiration based on window
                if window == 'minute':
                    self.redis_client.expire(key, 120)  # 2 minutes
                elif window == 'hour':
                    self.redis_client.expire(key, 7200)  # 2 hours
                else:  # day
                    self.redis_client.expire(key, 172800)  # 2 days
                    
            except Exception as e:
                logger.error(f"Error recording IP request in Redis: {e}")
    
    def _record_ip_request_cache(self, ip_address: str, action: str, current_time: int, success: bool):
        """Record IP-based request using Django cache."""
        time_windows = ['minute', 'hour', 'day']
        
        for window in time_windows:
            key = f"rate_limit:{action}:ip:{ip_address}:{window}"
            
            try:
                # Get existing timestamps
                timestamps = cache.get(key, [])
                
                # Add current timestamp
                timestamps.append(current_time)
                
                # Set timeout based on window
                if window == 'minute':
                    timeout = 120  # 2 minutes
                elif window == 'hour':
                    timeout = 7200  # 2 hours
                else:  # day
                    timeout = 172800  # 2 days
                
                # Save updated timestamps
                cache.set(key, timestamps, timeout)
                    
            except Exception as e:
                logger.error(f"Error recording IP request in cache: {e}")
    
    def _record_user_request(self, user_identifier: str, action: str, current_time: int, success: bool):
        """Record user-based request."""
        if self.redis_client:
            self._record_user_request_redis(user_identifier, action, current_time, success)
        else:
            self._record_user_request_cache(user_identifier, action, current_time, success)
    
    def _record_user_request_redis(self, user_identifier: str, action: str, current_time: int, success: bool):
        """Record user-based request using Redis."""
        time_windows = ['minute', 'hour', 'day']
        
        for window in time_windows:
            key = f"rate_limit:{action}:user:{user_identifier}:{window}"
            
            try:
                self.redis_client.zadd(key, {f"{current_time}:{success}": current_time})
                
                if window == 'minute':
                    self.redis_client.expire(key, 120)
                elif window == 'hour':
                    self.redis_client.expire(key, 7200)
                else:  # day
                    self.redis_client.expire(key, 172800)
                    
            except Exception as e:
                logger.error(f"Error recording user request in Redis: {e}")
    
    def _record_user_request_cache(self, user_identifier: str, action: str, current_time: int, success: bool):
        """Record user-based request using Django cache."""
        time_windows = ['minute', 'hour', 'day']
        
        for window in time_windows:
            key = f"rate_limit:{action}:user:{user_identifier}:{window}"
            
            try:
                # Get existing timestamps
                timestamps = cache.get(key, [])
                
                # Add current timestamp
                timestamps.append(current_time)
                
                # Set timeout based on window
                if window == 'minute':
                    timeout = 120  # 2 minutes
                elif window == 'hour':
                    timeout = 7200  # 2 hours
                else:  # day
                    timeout = 172800  # 2 days
                
                # Save updated timestamps
                cache.set(key, timestamps, timeout)
                    
            except Exception as e:
                logger.error(f"Error recording user request in cache: {e}")
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked."""
        try:
            from .models import BlockedIP
            blocked_ip = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).first()
            
            if blocked_ip:
                return blocked_ip.is_blocked()
            
            return False
        except Exception as e:
            logger.error(f"Error checking IP block status: {e}")
            return False
    
    def _log_attempt(self, request, action: str, user_identifier: str, is_limited: bool, timestamp: int):
        """Log attempt to database for security monitoring."""
        try:
            from .models import VisitorLog
            from django.contrib.auth.models import User
            
            ip_address = self.get_client_ip(request)
            user = None
            
            # Get user object if authenticated
            if request.user.is_authenticated:
                user = request.user
            elif user_identifier:
                try:
                    user = User.objects.filter(email=user_identifier).first()
                except:
                    pass
            
            VisitorLog.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                session_key=request.session.session_key,
                request_path=request.path,
                request_method=request.method,
                is_authenticated=request.user.is_authenticated,
                username_attempted=user_identifier,
                is_suspicious=is_limited,
                unix_timestamp=timestamp,
            )
        except Exception as e:
            logger.error(f"Error logging attempt: {e}")
    
    def _calculate_retry_after(self, ip_info: Dict, user_info: Dict) -> int:
        """Calculate retry-after delay in seconds."""
        delays = []
        
        # IP-based delays
        if ip_info.get('blocked_window') == 'minute':
            delays.append(60)
        elif ip_info.get('blocked_window') == 'hour':
            delays.append(3600)
        elif ip_info.get('blocked_window') == 'day':
            delays.append(86400)
        
        # User-based delays
        if user_info.get('blocked_window') == 'minute':
            delays.append(60)
        elif user_info.get('blocked_window') == 'hour':
            delays.append(3600)
        elif user_info.get('blocked_window') == 'day':
            delays.append(86400)
        
        return max(delays) if delays else 0
    
    def get_rate_limit_status(self, request, action: str = 'api', user_identifier: str = None) -> Dict:
        """Get current rate limit status without incrementing counters."""
        if not self.redis_client:
            return {}
        
        ip_address = self.get_client_ip(request)
        current_time = int(time.time())
        
        # Get IP status
        _, ip_info = self._check_ip_rate_limit(ip_address, action, current_time)
        
        # Get user status
        user_info = {}
        if user_identifier:
            _, user_info = self._check_user_rate_limit(user_identifier, action, current_time)
        
        return {
            'ip_address': ip_address,
            'ip_status': ip_info,
            'user_status': user_info,
            'timestamp': current_time,
        }
    
    def clear_rate_limit(self, ip_address: str = None, user_identifier: str = None, action: str = None):
        """Clear rate limiting data for debugging/admin purposes."""
        if not self.redis_client:
            return
        
        try:
            keys_to_delete = []
            
            if ip_address and action:
                keys_to_delete.extend([
                    f"rate_limit:{action}:ip:{ip_address}:minute",
                    f"rate_limit:{action}:ip:{ip_address}:hour",
                    f"rate_limit:{action}:ip:{ip_address}:day",
                ])
            
            if user_identifier and action:
                keys_to_delete.extend([
                    f"rate_limit:{action}:user:{user_identifier}:minute",
                    f"rate_limit:{action}:user:{user_identifier}:hour",
                    f"rate_limit:{action}:user:{user_identifier}:day",
                ])
            
            if keys_to_delete:
                self.redis_client.delete(*keys_to_delete)
                logger.info(f"Cleared rate limit data for keys: {keys_to_delete}")
        
        except Exception as e:
            logger.error(f"Error clearing rate limit data: {e}")


# Global instance
rate_limiter = RedisRateLimiter()
