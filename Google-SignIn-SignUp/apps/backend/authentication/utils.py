"""
Utility functions for JWT cookie handling and Google credential verification.
"""
import os
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
from google.oauth2 import id_token
import logging

logger = logging.getLogger(__name__)


class JWTCookieHelper:
    """Helper class for managing JWT tokens in HTTP-only cookies."""
    
    ACCESS_COOKIE_NAME = 'access_token'
    REFRESH_COOKIE_NAME = 'refresh_token'
    
    @classmethod
    def set_jwt_cookies(cls, response: HttpResponse, user) -> HttpResponse:
        """Set JWT access and refresh tokens as HTTP-only cookies."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Get token lifetimes from settings
        access_lifetime = getattr(settings, 'SIMPLE_JWT', {}).get(
            'ACCESS_TOKEN_LIFETIME', timedelta(minutes=15)
        )
        refresh_lifetime = getattr(settings, 'SIMPLE_JWT', {}).get(
            'REFRESH_TOKEN_LIFETIME', timedelta(days=7)
        )
        
        # Set access token cookie
        response.set_cookie(
            cls.ACCESS_COOKIE_NAME,
            access_token,
            max_age=int(access_lifetime.total_seconds()),
            httponly=True,
            secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
            samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
        )
        
        # Set refresh token cookie
        response.set_cookie(
            cls.REFRESH_COOKIE_NAME,
            refresh_token,
            max_age=int(refresh_lifetime.total_seconds()),
            httponly=True,
            secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
            samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
        )
        
        return response
    
    @classmethod
    def clear_jwt_cookies(cls, response: HttpResponse) -> HttpResponse:
        """Clear JWT cookies from response."""
        response.delete_cookie(cls.ACCESS_COOKIE_NAME)
        response.delete_cookie(cls.REFRESH_COOKIE_NAME)
        return response
    
    @classmethod
    def get_tokens_from_cookies(cls, request):
        """Extract JWT tokens from request cookies."""
        access_token = request.COOKIES.get(cls.ACCESS_COOKIE_NAME)
        refresh_token = request.COOKIES.get(cls.REFRESH_COOKIE_NAME)
        return access_token, refresh_token


class GoogleCredentialVerifier:
    """Helper class for verifying Google Identity Services credentials."""
    
    @classmethod
    def verify_credential(cls, credential: str) -> dict:
        """
        Verify Google credential and return user info.
        
        Args:
            credential: The credential string from Google Identity Services
            
        Returns:
            dict: User information from Google
            
        Raises:
            ValueError: If credential is invalid or verification fails
        """
        try:
            client_id = getattr(settings, 'GOOGLE_CLIENT_ID', os.getenv('GOOGLE_CLIENT_ID'))
            if not client_id:
                raise ValueError('Google Client ID not configured')
            
            # Verify the credential
            idinfo = id_token.verify_oauth2_token(
                credential, 
                requests.Request(), 
                client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False),
            }
            
        except ValueError as e:
            logger.error(f"Google credential verification failed: {str(e)}")
            raise ValueError(f"Invalid Google credential: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during Google credential verification: {str(e)}")
            raise ValueError("Failed to verify Google credential")
    
    @classmethod
    def get_or_create_user_from_google(cls, google_info: dict):
        """
        Get or create a Django user from Google user information.
        
        Args:
            google_info: User information from Google
            
        Returns:
            User: Django user instance
        """
        from django.contrib.auth.models import User
        
        email = google_info['email']
        
        try:
            # Try to get existing user by email
            user = User.objects.get(email=email)
            
            # Update user info if needed
            updated = False
            if not user.first_name and google_info.get('first_name'):
                user.first_name = google_info['first_name']
                updated = True
            if not user.last_name and google_info.get('last_name'):
                user.last_name = google_info['last_name']
                updated = True
            
            if updated:
                user.save()
                
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=google_info.get('first_name', ''),
                last_name=google_info.get('last_name', ''),
                # No password for Google users - they authenticate via Google
            )
            user.set_unusable_password()
            user.save()
        
        return user


class TwoFactorRateLimiter:
    """Rate limiter for Two-Factor Authentication attempts."""
    
    # Rate limiting configuration
    MAX_ATTEMPTS_PER_USER = 5  # Maximum attempts per user per time window
    MAX_ATTEMPTS_PER_IP = 10   # Maximum attempts per IP per time window
    TIME_WINDOW_MINUTES = 15   # Time window in minutes
    LOCKOUT_DURATION_MINUTES = 30  # How long to lock out after max attempts
    
    @classmethod
    def is_rate_limited(cls, user, ip_address=None):
        """
        Check if user or IP is rate limited for 2FA attempts.
        
        Args:
            user: Django User instance
            ip_address: Client IP address (optional)
            
        Returns:
            tuple: (is_limited, remaining_attempts, lockout_ends_at)
        """
        from django.utils import timezone
        from datetime import timedelta
        from .models import TwoFactorAttempt
        
        now = timezone.now()
        time_window_start = now - timedelta(minutes=cls.TIME_WINDOW_MINUTES)
        lockout_end = now - timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
        
        # Check user-based rate limiting
        user_attempts = TwoFactorAttempt.objects.filter(
            user=user,
            created_at__gte=time_window_start,
            success=False
        ).count()
        
        # Check for recent lockout period
        recent_failures = TwoFactorAttempt.objects.filter(
            user=user,
            created_at__gte=lockout_end,
            success=False
        ).count()
        
        # If user has too many recent failures, check if still in lockout
        if recent_failures >= cls.MAX_ATTEMPTS_PER_USER:
            last_failure = TwoFactorAttempt.objects.filter(
                user=user,
                success=False
            ).order_by('-created_at').first()
            
            if last_failure:
                lockout_ends_at = last_failure.created_at + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
                if now < lockout_ends_at:
                    return True, 0, lockout_ends_at
        
        # Check current window attempts
        if user_attempts >= cls.MAX_ATTEMPTS_PER_USER:
            # Calculate when lockout ends
            lockout_ends_at = now + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
            return True, 0, lockout_ends_at
        
        # Check IP-based rate limiting (if IP provided)
        if ip_address:
            ip_attempts = TwoFactorAttempt.objects.filter(
                ip_address=ip_address,
                created_at__gte=time_window_start,
                success=False
            ).count()
            
            if ip_attempts >= cls.MAX_ATTEMPTS_PER_IP:
                lockout_ends_at = now + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
                return True, 0, lockout_ends_at
        
        # Calculate remaining attempts
        remaining_attempts = cls.MAX_ATTEMPTS_PER_USER - user_attempts
        
        return False, remaining_attempts, None
    
    @classmethod
    def log_attempt(cls, user, ip_address, success, attempt_type='totp'):
        """
        Log a 2FA verification attempt.
        
        Args:
            user: Django User instance
            ip_address: Client IP address
            success: Boolean indicating if attempt was successful
            attempt_type: Type of attempt ('totp' or 'backup')
        """
        from .models import TwoFactorAttempt
        
        try:
            TwoFactorAttempt.objects.create(
                user=user,
                ip_address=ip_address or '0.0.0.0',
                success=success,
                attempt_type=attempt_type
            )
        except Exception as e:
            # Don't fail the request if logging fails
            logger.error(f"Failed to log 2FA attempt: {str(e)}")
    
    @classmethod
    def clean_old_attempts(cls, days_to_keep=30):
        """
        Clean up old 2FA attempt records to prevent database bloat.
        
        Args:
            days_to_keep: Number of days of records to keep
        """
        from django.utils import timezone
        from datetime import timedelta
        from .models import TwoFactorAttempt
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        deleted_count = TwoFactorAttempt.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old 2FA attempt records")
        return deleted_count
    
    @classmethod
    def get_rate_limit_message(cls, remaining_attempts, lockout_ends_at):
        """
        Generate user-friendly rate limit message.
        
        Args:
            remaining_attempts: Number of attempts remaining
            lockout_ends_at: When the lockout ends (if applicable)
            
        Returns:
            str: User-friendly message
        """
        if lockout_ends_at:
            from django.utils import timezone
            
            time_left = lockout_ends_at - timezone.now()
            minutes_left = int(time_left.total_seconds() / 60)
            
            if minutes_left <= 0:
                return "Too many failed attempts. Please try again."
            elif minutes_left == 1:
                return "Too many failed attempts. Please try again in 1 minute."
            else:
                return f"Too many failed attempts. Please try again in {minutes_left} minutes."
        else:
            if remaining_attempts == 1:
                return f"Invalid code. You have {remaining_attempts} attempt remaining."
            else:
                return f"Invalid code. You have {remaining_attempts} attempts remaining."