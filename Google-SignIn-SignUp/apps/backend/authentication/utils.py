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
