from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from .serializers import (
    RegisterSerializer, LoginSerializer, GoogleLoginSerializer, 
    UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .utils import JWTCookieHelper, GoogleCredentialVerifier
from .email_service import email_service
from .recaptcha_utils import verify_recaptcha_token
from .rate_limiter import rate_limiter
from .decorators import login_rate_limit, register_rate_limit, password_reset_rate_limit, two_factor_rate_limit

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@register_rate_limit
def register_view(request):
    """Register a new user with email and password."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        # Verify reCAPTCHA token if provided
        recaptcha_token = serializer.validated_data.get('recaptcha_token')
        if recaptcha_token:
            is_valid, recaptcha_result = verify_recaptcha_token(
                request, recaptcha_token, action='signup'
            )
            if not is_valid:
                logger.warning(f"reCAPTCHA verification failed for registration: {recaptcha_result}")
                return Response({
                    'error': 'Security verification failed. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Send welcome email via SendinBlue
        try:
            user_name = user.get_full_name() or user.first_name or user.email.split('@')[0]
            email_sent = email_service.send_welcome_email(
                to_email=user.email,
                to_name=user_name
            )
            
            if email_sent:
                logger.info(f"Welcome email sent successfully via SendinBlue to {user.email}")
            else:
                logger.warning(f"Failed to send welcome email via SendinBlue to {user.email}")
                
        except Exception as e:
            logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
        
        # Create response with user data
        user_serializer = UserSerializer(user)
        response = Response({
            'user': user_serializer.data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
        
        # Set JWT cookies
        response = JWTCookieHelper.set_jwt_cookies(response, user)
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@login_rate_limit
def login_view(request):
    """Login user with email and password."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        # Verify reCAPTCHA token if provided
        recaptcha_token = serializer.validated_data.get('recaptcha_token')
        if recaptcha_token:
            is_valid, recaptcha_result = verify_recaptcha_token(
                request, recaptcha_token, action='login'
            )
            if not is_valid:
                logger.warning(f"reCAPTCHA verification failed for login: {recaptcha_result}")
                return Response({
                    'error': 'Security verification failed. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        # Check if user has 2FA enabled
        try:
            two_factor = user.two_factor
            requires_2fa = two_factor.is_enabled
        except:
            requires_2fa = False
        
        user_serializer = UserSerializer(user)
        
        if requires_2fa:
            # Create temporary token for 2FA verification
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            temp_token = str(refresh.access_token)
            
            # Store temporary token in response (not as HTTP-only cookie)
            response = Response({
                'requires_2fa': True,
                'temp_token': temp_token,
                'user_id': user.id,
                'message': 'Please provide your 2FA code to complete login.',
                'backup_codes_available': two_factor.backup_tokens_count > 0
            }, status=status.HTTP_200_OK)
            
            logger.info(f"Login requires 2FA for user {user.email}")
        else:
            # Standard login flow without 2FA
            response = Response({
                'user': user_serializer.data,
                'message': 'Login successful',
                'requires_2fa': False
            }, status=status.HTTP_200_OK)
            
            # Set JWT cookies for full authentication
            response = JWTCookieHelper.set_jwt_cookies(response, user)
            
            logger.info(f"Login successful for user {user.email} (no 2FA)")
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@login_rate_limit
def google_login_view(request):
    """Login or register user with Google credential."""
    serializer = GoogleLoginSerializer(data=request.data)
    if serializer.is_valid():
        credential = serializer.validated_data['credential']
        
        try:
            # Verify Google credential
            google_info = GoogleCredentialVerifier.verify_credential(credential)
            
            # Get or create user
            user = GoogleCredentialVerifier.get_or_create_user_from_google(google_info)
            
            # Create response with user data
            user_serializer = UserSerializer(user)
            response = Response({
                'user': user_serializer.data,
                'message': 'Google login successful'
            }, status=status.HTTP_200_OK)
            
            # Set JWT cookies
            response = JWTCookieHelper.set_jwt_cookies(response, user)
            
            return response
            
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response({
                'error': 'Google login failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    """Refresh JWT tokens using refresh token from cookies."""
    access_token, refresh_token = JWTCookieHelper.get_tokens_from_cookies(request)
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token not found'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Validate and refresh the token
        refresh = RefreshToken(refresh_token)
        user = refresh.user
        
        # Create new tokens
        new_refresh = RefreshToken.for_user(user)
        
        response = Response({
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)
        
        # Set new JWT cookies
        response = JWTCookieHelper.set_jwt_cookies(response, user)
        
        return response
        
    except (TokenError, InvalidToken) as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response({
            'error': 'Token refresh failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Get current authenticated user information."""
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user and clear JWT cookies."""
    try:
        # Get refresh token from cookies
        access_token, refresh_token = JWTCookieHelper.get_tokens_from_cookies(request)
        
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
    
    except Exception as e:
        # Log error but don't fail logout
        logger.warning(f"Error blacklisting token during logout: {str(e)}")
    
    response = Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)
    
    # Clear JWT cookies
    response = JWTCookieHelper.clear_jwt_cookies(response)
    
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_view(request):
    """Health check endpoint."""
    return Response({
        'status': 'OK',
        'message': 'Django Auth Backend is running'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@password_reset_rate_limit
def forgot_password_view(request):
    """Send password reset email to user."""
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        # Verify reCAPTCHA token if provided
        recaptcha_token = serializer.validated_data.get('recaptcha_token')
        if recaptcha_token:
            is_valid, recaptcha_result = verify_recaptcha_token(
                request, recaptcha_token, action='forgot_password'
            )
            if not is_valid:
                logger.warning(f"reCAPTCHA verification failed for forgot password: {recaptcha_result}")
                return Response({
                    'error': 'Security verification failed. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_token = f"{uid}-{token}"
            
            # Create reset URL (for development, we'll use localhost:3007)
            reset_url = f"http://localhost:3007/reset-password?token={reset_token}"
            
            # Get user's display name
            user_name = user.get_full_name() or user.first_name or user.email.split('@')[0]
            
            # Send email using SendinBlue
            try:
                email_sent = email_service.send_password_reset_email(
                    to_email=email,
                    to_name=user_name,
                    reset_url=reset_url
                )
                
                if email_sent:
                    logger.info(f"Password reset email sent successfully via SendinBlue to {email}")
                else:
                    logger.error(f"Failed to send password reset email via SendinBlue to {email}")
                    # Fallback: print to console for development
                    print(f"=== PASSWORD RESET EMAIL (SendinBlue Failed) ===")
                    print(f"To: {email} ({user_name})")
                    print(f"Reset URL: {reset_url}")
                    print(f"============================================")
                    
            except Exception as e:
                logger.error(f"SendinBlue service error when sending email to {email}: {str(e)}")
                # Fallback: print to console for development
                print(f"=== PASSWORD RESET EMAIL (SendinBlue Error) ===")
                print(f"To: {email} ({user_name})")
                print(f"Reset URL: {reset_url}")
                print(f"Error: {str(e)}")
                print(f"===========================================")
                
        except User.DoesNotExist:
            # Don't reveal whether email exists for security
            logger.info(f"Password reset requested for non-existent email: {email}")
        
        # Always return success message for security
        return Response({
            'message': 'If an account with that email exists, password reset instructions have been sent.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@password_reset_rate_limit
def reset_password_view(request):
    """Reset user password with token."""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        # Verify reCAPTCHA token if provided
        recaptcha_token = serializer.validated_data.get('recaptcha_token')
        if recaptcha_token:
            is_valid, recaptcha_result = verify_recaptcha_token(
                request, recaptcha_token, action='reset_password'
            )
            if not is_valid:
                logger.warning(f"reCAPTCHA verification failed for password reset: {recaptcha_result}")
                return Response({
                    'error': 'Security verification failed. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['password']
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password reset successful for user {user.email}")
        
        return Response({
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_setup_view(request):
    """Setup Two-Factor Authentication - generate secret and return QR code URI."""
    from .serializers import TwoFactorSetupSerializer
    
    serializer = TwoFactorSetupSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        
        try:
            from .models import UserTwoFactor
            import pyotp
            import qrcode
            from io import BytesIO
            import base64
            
            # Get or create UserTwoFactor record
            two_factor, created = UserTwoFactor.objects.get_or_create(user=user)
            
            # Generate new secret if needed or if 2FA is not enabled
            if not two_factor.get_secret_key() or not two_factor.is_enabled:
                secret_key = pyotp.random_base32()
                two_factor.set_secret_key(secret_key)
                two_factor.is_enabled = False  # Keep disabled until verification
                two_factor.save()
            else:
                secret_key = two_factor.get_secret_key()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret_key)
            
            # Generate QR code URI
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="Secure Authentication App"
            )
            
            # Generate QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to base64 string
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"2FA setup initiated for user {user.email}")
            
            return Response({
                'secret_key': secret_key,
                'qr_code_uri': provisioning_uri,
                'qr_code_image': f"data:image/png;base64,{qr_code_data}",
                'message': 'Scan the QR code with your authenticator app, then verify with a code to enable 2FA.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"2FA setup error for user {user.email}: {str(e)}")
            return Response({
                'error': 'Failed to setup Two-Factor Authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_enable_view(request):
    """Enable Two-Factor Authentication after verifying TOTP code."""
    from .serializers import TwoFactorEnableSerializer
    
    serializer = TwoFactorEnableSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        two_factor = serializer.validated_data['two_factor']
        
        try:
            from django.utils import timezone
            
            # Enable 2FA
            two_factor.is_enabled = True
            two_factor.last_used_at = timezone.now()
            two_factor.save()
            
            # Generate backup codes
            backup_codes = two_factor.generate_backup_codes()
            
            logger.info(f"2FA enabled for user {user.email}")
            
            return Response({
                'message': '2FA has been successfully enabled for your account.',
                'backup_codes': backup_codes,
                'backup_codes_message': 'Save these backup codes in a secure place. Each code can only be used once.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"2FA enable error for user {user.email}: {str(e)}")
            return Response({
                'error': 'Failed to enable Two-Factor Authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_verify_view(request):
    """Verify TOTP code or backup code."""
    from .serializers import TwoFactorVerifySerializer
    from .utils import TwoFactorRateLimiter
    from .recaptcha_utils import RecaptchaVerifier
    
    user = request.user
    client_ip = RecaptchaVerifier.get_client_ip(request)
    
    # Check rate limiting before processing
    is_limited, remaining_attempts, lockout_ends_at = TwoFactorRateLimiter.is_rate_limited(user, client_ip)
    
    if is_limited:
        message = TwoFactorRateLimiter.get_rate_limit_message(remaining_attempts, lockout_ends_at)
        logger.warning(f"2FA rate limit exceeded for user {user.email} from IP {client_ip}")
        
        return Response({
            'error': message,
            'rate_limited': True,
            'remaining_attempts': remaining_attempts,
            'lockout_ends_at': lockout_ends_at.isoformat() if lockout_ends_at else None
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    serializer = TwoFactorVerifySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        two_factor = serializer.validated_data['two_factor']
        verification_method = serializer.validated_data['verification_method']
        
        try:
            from django.utils import timezone
            
            # Mark backup code as used if it was used
            if verification_method == 'backup':
                backup_code_obj = serializer.validated_data['backup_code_obj']
                backup_code_obj.mark_as_used()
            
            # Update last used timestamp
            two_factor.last_used_at = timezone.now()
            two_factor.save()
            
            # Log successful attempt
            TwoFactorRateLimiter.log_attempt(user, client_ip, True, verification_method)
            
            logger.info(f"2FA verification successful for user {user.email} using {verification_method}")
            
            return Response({
                'message': '2FA verification successful.',
                'verification_method': verification_method,
                'remaining_backup_codes': two_factor.backup_tokens_count if verification_method == 'backup' else None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"2FA verification error for user {user.email}: {str(e)}")
            return Response({
                'error': 'Failed to verify Two-Factor Authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Log failed attempt and provide rate limit info
    totp_code = request.data.get('totp_code')
    backup_code = request.data.get('backup_code')
    attempt_type = 'totp' if totp_code else 'backup' if backup_code else 'unknown'
    
    TwoFactorRateLimiter.log_attempt(user, client_ip, False, attempt_type)
    
    # Check rate limiting again after failed attempt
    is_limited, remaining_attempts, lockout_ends_at = TwoFactorRateLimiter.is_rate_limited(user, client_ip)
    
    # Add rate limiting info to error response
    error_response = dict(serializer.errors)
    error_response['remaining_attempts'] = remaining_attempts
    
    if is_limited:
        message = TwoFactorRateLimiter.get_rate_limit_message(remaining_attempts, lockout_ends_at)
        error_response['rate_limit_message'] = message
        error_response['rate_limited'] = True
        error_response['lockout_ends_at'] = lockout_ends_at.isoformat() if lockout_ends_at else None
        return Response(error_response, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_disable_view(request):
    """Disable Two-Factor Authentication."""
    from .serializers import TwoFactorDisableSerializer
    
    serializer = TwoFactorDisableSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        two_factor = serializer.validated_data['two_factor']
        
        try:
            # Mark backup code as used if it was used for verification
            if 'backup_code_obj' in serializer.validated_data:
                backup_code_obj = serializer.validated_data['backup_code_obj']
                backup_code_obj.mark_as_used()
            
            # Disable 2FA and clear sensitive data
            two_factor.is_enabled = False
            two_factor.set_secret_key(None)  # Clear the secret
            two_factor.backup_tokens_count = 0
            two_factor.save()
            
            # Delete all backup codes
            two_factor.backup_codes.all().delete()
            
            logger.info(f"2FA disabled for user {user.email}")
            
            return Response({
                'message': '2FA has been successfully disabled for your account.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"2FA disable error for user {user.email}: {str(e)}")
            return Response({
                'error': 'Failed to disable Two-Factor Authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def two_factor_status_view(request):
    """Get Two-Factor Authentication status for current user."""
    from .serializers import TwoFactorStatusSerializer
    
    user = request.user
    
    try:
        two_factor = user.two_factor
        serializer = TwoFactorStatusSerializer(two_factor)
    except:
        # No 2FA setup yet
        serializer = TwoFactorStatusSerializer(None)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@two_factor_rate_limit
def two_factor_login_complete_view(request):
    """Complete login process after 2FA verification."""
    from .utils import TwoFactorRateLimiter
    from .recaptcha_utils import RecaptchaVerifier
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    # Required fields
    temp_token = request.data.get('temp_token')
    totp_code = request.data.get('totp_code')
    backup_code = request.data.get('backup_code')
    user_id = request.data.get('user_id')
    
    if not temp_token or not user_id:
        return Response({
            'error': 'Temporary token and user ID are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not totp_code and not backup_code:
        return Response({
            'error': 'Either TOTP code or backup code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if totp_code and backup_code:
        return Response({
            'error': 'Please provide either TOTP code or backup code, not both.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify temporary token
        access_token = AccessToken(temp_token)
        token_user_id = access_token.get('user_id')
        
        if str(token_user_id) != str(user_id):
            return Response({
                'error': 'Invalid token or user ID mismatch.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        user = User.objects.get(id=user_id)
        
    except (InvalidToken, TokenError, User.DoesNotExist):
        return Response({
            'error': 'Invalid or expired temporary token.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has 2FA enabled
    try:
        two_factor = user.two_factor
        if not two_factor.is_enabled:
            return Response({
                'error': '2FA is not enabled for this account.'
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'error': '2FA is not enabled for this account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check rate limiting
    client_ip = RecaptchaVerifier.get_client_ip(request)
    is_limited, remaining_attempts, lockout_ends_at = TwoFactorRateLimiter.is_rate_limited(user, client_ip)
    
    if is_limited:
        message = TwoFactorRateLimiter.get_rate_limit_message(remaining_attempts, lockout_ends_at)
        logger.warning(f"2FA login rate limit exceeded for user {user.email} from IP {client_ip}")
        
        return Response({
            'error': message,
            'rate_limited': True,
            'remaining_attempts': remaining_attempts,
            'lockout_ends_at': lockout_ends_at.isoformat() if lockout_ends_at else None
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Verify 2FA code
    verification_successful = False
    verification_method = None
    backup_code_obj = None
    
    if totp_code:
        # Verify TOTP code
        if not totp_code.isdigit() or len(totp_code) != 6:
            TwoFactorRateLimiter.log_attempt(user, client_ip, False, 'totp')
            return Response({
                'error': 'TOTP code must be a 6-digit number.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        secret_key = two_factor.get_secret_key()
        if not secret_key:
            return Response({
                'error': '2FA configuration error. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        import pyotp
        totp = pyotp.TOTP(secret_key)
        if totp.verify(totp_code, valid_window=1):
            verification_successful = True
            verification_method = 'totp'
    
    elif backup_code:
        # Verify backup code
        for bc in two_factor.backup_codes.filter(is_used=False):
            if bc.verify_code(backup_code):
                verification_successful = True
                verification_method = 'backup'
                backup_code_obj = bc
                break
    
    if not verification_successful:
        # Log failed attempt
        attempt_type = 'totp' if totp_code else 'backup'
        TwoFactorRateLimiter.log_attempt(user, client_ip, False, attempt_type)
        
        # Check rate limiting again after failed attempt
        is_limited, remaining_attempts, lockout_ends_at = TwoFactorRateLimiter.is_rate_limited(user, client_ip)
        
        error_response = {
            'error': 'Invalid 2FA code. Please try again.',
            'remaining_attempts': remaining_attempts
        }
        
        if is_limited:
            message = TwoFactorRateLimiter.get_rate_limit_message(remaining_attempts, lockout_ends_at)
            error_response['rate_limit_message'] = message
            error_response['rate_limited'] = True
            error_response['lockout_ends_at'] = lockout_ends_at.isoformat() if lockout_ends_at else None
            return Response(error_response, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
    
    # 2FA verification successful - complete login
    try:
        from django.utils import timezone
        
        # Mark backup code as used if it was used
        if backup_code_obj:
            backup_code_obj.mark_as_used()
        
        # Update last used timestamp
        two_factor.last_used_at = timezone.now()
        two_factor.save()
        
        # Log successful attempt
        TwoFactorRateLimiter.log_attempt(user, client_ip, True, verification_method)
        
        # Create response with user data
        user_serializer = UserSerializer(user)
        response = Response({
            'user': user_serializer.data,
            'message': '2FA login completed successfully.',
            'verification_method': verification_method,
            'remaining_backup_codes': two_factor.backup_tokens_count if verification_method == 'backup' else None
        }, status=status.HTTP_200_OK)
        
        # Set JWT cookies for full authentication
        response = JWTCookieHelper.set_jwt_cookies(response, user)
        
        logger.info(f"2FA login completed for user {user.email} using {verification_method}")
        
        return response
        
    except Exception as e:
        logger.error(f"2FA login completion error for user {user.email}: {str(e)}")
        return Response({
            'error': 'Failed to complete login process'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)