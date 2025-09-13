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

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
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
        
        # Create response with user data
        user_serializer = UserSerializer(user)
        response = Response({
            'user': user_serializer.data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
        # Set JWT cookies
        response = JWTCookieHelper.set_jwt_cookies(response, user)
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
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