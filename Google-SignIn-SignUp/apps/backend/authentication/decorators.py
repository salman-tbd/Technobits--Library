"""
Rate limiting decorators for authentication views.
"""
import functools
import logging
from django.http import JsonResponse
from .rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


def rate_limit(action='api', per_user=True, per_ip=True, fail_on_limit=True):
    """
    Decorator to apply rate limiting to views.
    
    Args:
        action: Action type for rate limiting ('login', 'register', 'api', etc.)
        per_user: Whether to apply per-user rate limiting
        per_ip: Whether to apply per-IP rate limiting
        fail_on_limit: Whether to return error response when rate limit exceeded
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Skip rate limiting if middleware already handled it
            if hasattr(request, 'rate_limit_checked'):
                return view_func(request, *args, **kwargs)
            
            # Get user identifier
            user_identifier = None
            if per_user:
                if request.user.is_authenticated:
                    user_identifier = request.user.email or request.user.username
                elif request.method == 'POST':
                    # Try to extract email from request data
                    if hasattr(request, 'data') and 'email' in request.data:
                        user_identifier = request.data['email']
                    elif 'email' in request.POST:
                        user_identifier = request.POST['email']
            
            # Check rate limits
            if per_ip or per_user:
                is_limited, rate_limit_info = rate_limiter.check_rate_limit(
                    request=request,
                    action=action,
                    user_identifier=user_identifier
                )
                
                if is_limited and fail_on_limit:
                    retry_after = rate_limit_info.get('retry_after', 60)
                    
                    # Determine reason
                    reasons = []
                    if rate_limit_info.get('ip_limited'):
                        reasons.append("Too many requests from your IP")
                    if rate_limit_info.get('user_limited'):
                        reasons.append("Too many requests for this account")
                    if rate_limit_info.get('ip_blocked'):
                        reasons.append("IP address temporarily blocked")
                    
                    reason = ". ".join(reasons) if reasons else "Rate limit exceeded"
                    
                    logger.warning(
                        f"Rate limit exceeded for {action}: "
                        f"{rate_limiter.get_client_ip(request)} - {reason}"
                    )
                    
                    response = JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f"{reason}. Please try again later.",
                        'retry_after': retry_after,
                        'action': action,
                    }, status=429)
                    
                    response['Retry-After'] = str(retry_after)
                    response['X-RateLimit-Exceeded'] = 'true'
                    
                    return response
                
                # Store rate limit info for later use
                request.rate_limit_info = rate_limit_info
            
            # Mark as checked to avoid double-checking in middleware
            request.rate_limit_checked = True
            
            # Call the original view
            response = view_func(request, *args, **kwargs)
            
            # Record the request
            success = 200 <= response.status_code < 400
            rate_limiter.record_request(
                request=request,
                action=action,
                user_identifier=user_identifier,
                success=success
            )
            
            return response
        
        return wrapper
    return decorator


def login_rate_limit(view_func):
    """Specific rate limiter for login endpoints."""
    return rate_limit(action='login', per_user=True, per_ip=True)(view_func)


def register_rate_limit(view_func):
    """Specific rate limiter for registration endpoints."""
    return rate_limit(action='register', per_user=True, per_ip=True)(view_func)


def password_reset_rate_limit(view_func):
    """Specific rate limiter for password reset endpoints."""
    return rate_limit(action='password_reset', per_user=True, per_ip=True)(view_func)


def two_factor_rate_limit(view_func):
    """Specific rate limiter for 2FA endpoints."""
    return rate_limit(action='2fa', per_user=True, per_ip=True)(view_func)
