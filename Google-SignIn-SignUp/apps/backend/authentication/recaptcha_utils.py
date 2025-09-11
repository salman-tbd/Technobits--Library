"""
reCAPTCHA v3 verification utilities for Django backend.
"""
import requests
import logging
from django.conf import settings
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class RecaptchaVerifier:
    """
    Utility class for verifying Google reCAPTCHA v3 tokens.
    """
    
    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
    DEFAULT_MIN_SCORE = 0.5  # Minimum score for reCAPTCHA v3 (0.0 = bot, 1.0 = human)
    
    @classmethod
    def verify_token(
        cls, 
        token: str, 
        action: Optional[str] = None,
        min_score: Optional[float] = None,
        remote_ip: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify reCAPTCHA token with Google's API.
        
        Args:
            token: reCAPTCHA token from frontend
            action: Expected action name (optional for v3)
            min_score: Minimum score required (default: 0.5)
            remote_ip: Client's IP address (optional)
            
        Returns:
            Tuple of (is_valid, response_data)
        """
        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if not secret_key:
            logger.error("RECAPTCHA_SECRET_KEY not configured in settings")
            return False, {'error': 'reCAPTCHA not configured'}
        
        if not token:
            logger.warning("Empty reCAPTCHA token provided")
            return False, {'error': 'No reCAPTCHA token provided'}
        
        # Prepare verification request
        data = {
            'secret': secret_key,
            'response': token,
        }
        
        if remote_ip:
            data['remoteip'] = remote_ip
            
        try:
            # Make request to Google's verification endpoint
            response = requests.post(
                cls.VERIFY_URL,
                data=data,
                timeout=10,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Log the verification attempt
            logger.info(f"reCAPTCHA verification: success={result.get('success', False)}, "
                       f"score={result.get('score', 'N/A')}, action={result.get('action', 'N/A')}")
            
            # Check if verification was successful
            if not result.get('success', False):
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                return False, {
                    'error': 'reCAPTCHA verification failed',
                    'error_codes': error_codes
                }
            
            # For reCAPTCHA v3, check the score
            score = result.get('score')
            if score is not None:
                min_required_score = min_score or cls.DEFAULT_MIN_SCORE
                if score < min_required_score:
                    logger.warning(f"reCAPTCHA score too low: {score} < {min_required_score}")
                    return False, {
                        'error': 'reCAPTCHA score too low',
                        'score': score,
                        'min_score': min_required_score
                    }
            
            # Check action if specified (reCAPTCHA v3)
            if action and result.get('action') != action:
                logger.warning(f"reCAPTCHA action mismatch: expected={action}, got={result.get('action')}")
                return False, {
                    'error': 'reCAPTCHA action mismatch',
                    'expected': action,
                    'actual': result.get('action')
                }
            
            # Verification successful
            return True, result
            
        except requests.RequestException as e:
            logger.error(f"reCAPTCHA verification request failed: {str(e)}")
            return False, {'error': 'reCAPTCHA service unavailable'}
        
        except Exception as e:
            logger.error(f"Unexpected error during reCAPTCHA verification: {str(e)}")
            return False, {'error': 'reCAPTCHA verification error'}
    
    @classmethod
    def is_required(cls) -> bool:
        """
        Check if reCAPTCHA verification is required based on settings.
        
        Returns:
            True if reCAPTCHA is configured and should be enforced
        """
        return bool(getattr(settings, 'RECAPTCHA_SECRET_KEY', None)) and \
               getattr(settings, 'RECAPTCHA_ENABLED', True)
    
    @classmethod
    def get_client_ip(cls, request) -> Optional[str]:
        """
        Extract client IP address from Django request.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            Client IP address or None
        """
        # Check for forwarded IP first (behind proxy/load balancer)
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header
        real_ip = request.META.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request.META.get('REMOTE_ADDR')


def verify_recaptcha_token(
    request, 
    token: str, 
    action: Optional[str] = None,
    min_score: Optional[float] = None
) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to verify reCAPTCHA token from a Django request.
    
    Args:
        request: Django HttpRequest object
        token: reCAPTCHA token from frontend
        action: Expected action name
        min_score: Minimum score required
        
    Returns:
        Tuple of (is_valid, response_data)
    """
    if not RecaptchaVerifier.is_required():
        logger.info("reCAPTCHA verification skipped (not configured or disabled)")
        return True, {'message': 'reCAPTCHA verification skipped'}
    
    client_ip = RecaptchaVerifier.get_client_ip(request)
    return RecaptchaVerifier.verify_token(
        token=token,
        action=action,
        min_score=min_score,
        remote_ip=client_ip
    )
