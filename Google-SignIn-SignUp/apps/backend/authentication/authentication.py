"""
Custom JWT authentication class that reads tokens from HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from .utils import JWTCookieHelper


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads access tokens from HTTP-only cookies.
    Falls back to standard Authorization header if cookie is not present.
    """
    
    def authenticate(self, request):
        # First try to get token from cookie
        access_token, _ = JWTCookieHelper.get_tokens_from_cookies(request)
        
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return (user, validated_token)
            except (InvalidToken, TokenError):
                # Token from cookie is invalid, try header
                pass
        
        # Fall back to standard header-based authentication
        return super().authenticate(request)
