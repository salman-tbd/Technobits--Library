from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Combine first_name and last_name into 'name' field
        name_parts = [instance.first_name, instance.last_name]
        data['name'] = ' '.join(filter(None, name_parts)) or None
        # Remove individual name fields
        data.pop('first_name', None)
        data.pop('last_name', None)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(required=False, allow_blank=True)
    recaptcha_token = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'recaptcha_token')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name', '')
        email = validated_data['email']
        password = validated_data['password']
        
        # Split name into first and last name
        name_parts = name.strip().split() if name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    recaptcha_token = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')

        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField()

    def validate_credential(self, value):
        if not value:
            raise serializers.ValidationError('Google credential is required.')
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    recaptcha_token = serializers.CharField(required=False)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        except User.DoesNotExist:
            # Don't reveal whether email exists for security
            pass
        return value


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(validators=[validate_password])
    recaptcha_token = serializers.CharField(required=False)

    def validate(self, attrs):
        token = attrs.get('token')
        
        try:
            # Decode the token to get user ID
            uid = force_str(urlsafe_base64_decode(token.split('-')[0]))
            user = User.objects.get(pk=uid)
            
            # Verify the token
            token_part = '-'.join(token.split('-')[1:])
            if not default_token_generator.check_token(user, token_part):
                raise serializers.ValidationError('Invalid or expired reset token.')
            
            attrs['user'] = user
        except (ValueError, User.DoesNotExist, IndexError):
            raise serializers.ValidationError('Invalid or expired reset token.')
        
        return attrs


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for initiating Two-Factor Authentication setup."""
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Check if user already has 2FA enabled
        try:
            two_factor = user.two_factor
            if two_factor.is_enabled:
                raise serializers.ValidationError('Two-Factor Authentication is already enabled for this account.')
        except:
            # UserTwoFactor doesn't exist yet, which is fine
            pass
        
        return attrs


class TwoFactorEnableSerializer(serializers.Serializer):
    """Serializer for enabling Two-Factor Authentication after setup verification."""
    
    totp_code = serializers.CharField(min_length=6, max_length=6)
    
    def validate_totp_code(self, value):
        # Validate that it's a 6-digit number
        if not value.isdigit():
            raise serializers.ValidationError('TOTP code must be a 6-digit number.')
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        totp_code = attrs['totp_code']
        
        # Check if user has a pending 2FA setup
        try:
            two_factor = user.two_factor
            if two_factor.is_enabled:
                raise serializers.ValidationError('Two-Factor Authentication is already enabled.')
            
            secret_key = two_factor.get_secret_key()
            if not secret_key:
                raise serializers.ValidationError('No pending 2FA setup found. Please start the setup process again.')
        except:
            raise serializers.ValidationError('No pending 2FA setup found. Please start the setup process first.')
        
        # Verify the TOTP code
        import pyotp
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(totp_code, valid_window=1):  # Allow 1 time step tolerance
            raise serializers.ValidationError('Invalid TOTP code. Please check your authenticator app and try again.')
        
        attrs['two_factor'] = two_factor
        return attrs


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for verifying TOTP codes during login or sensitive operations."""
    
    totp_code = serializers.CharField(required=False, min_length=6, max_length=8)
    backup_code = serializers.CharField(required=False, min_length=8, max_length=8)
    
    def validate(self, attrs):
        totp_code = attrs.get('totp_code')
        backup_code = attrs.get('backup_code')
        
        # Must provide either TOTP code or backup code
        if not totp_code and not backup_code:
            raise serializers.ValidationError('Either TOTP code or backup code is required.')
        
        if totp_code and backup_code:
            raise serializers.ValidationError('Please provide either TOTP code or backup code, not both.')
        
        user = self.context['request'].user
        
        # Check if user has 2FA enabled
        try:
            two_factor = user.two_factor
            if not two_factor.is_enabled:
                raise serializers.ValidationError('Two-Factor Authentication is not enabled for this account.')
        except:
            raise serializers.ValidationError('Two-Factor Authentication is not enabled for this account.')
        
        if totp_code:
            # Verify TOTP code
            secret_key = two_factor.get_secret_key()
            if not secret_key:
                raise serializers.ValidationError('2FA configuration error. Please contact support.')
            
            import pyotp
            totp = pyotp.TOTP(secret_key)
            if not totp.verify(totp_code, valid_window=1):
                raise serializers.ValidationError('Invalid TOTP code. Please check your authenticator app and try again.')
            
            attrs['verification_method'] = 'totp'
        
        elif backup_code:
            # Verify backup code
            backup_code_obj = None
            for bc in two_factor.backup_codes.filter(is_used=False):
                if bc.verify_code(backup_code):
                    backup_code_obj = bc
                    break
            
            if not backup_code_obj:
                raise serializers.ValidationError('Invalid or already used backup code.')
            
            attrs['backup_code_obj'] = backup_code_obj
            attrs['verification_method'] = 'backup'
        
        attrs['two_factor'] = two_factor
        return attrs


class TwoFactorDisableSerializer(serializers.Serializer):
    """Serializer for disabling Two-Factor Authentication."""
    
    password = serializers.CharField(write_only=True)
    totp_code = serializers.CharField(required=False, min_length=6, max_length=6)
    backup_code = serializers.CharField(required=False, min_length=8, max_length=8)
    
    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Invalid password.')
        return value
    
    def validate(self, attrs):
        totp_code = attrs.get('totp_code')
        backup_code = attrs.get('backup_code')
        
        # Must provide either TOTP code or backup code for additional security
        if not totp_code and not backup_code:
            raise serializers.ValidationError('Either TOTP code or backup code is required to disable 2FA.')
        
        if totp_code and backup_code:
            raise serializers.ValidationError('Please provide either TOTP code or backup code, not both.')
        
        user = self.context['request'].user
        
        # Check if user has 2FA enabled
        try:
            two_factor = user.two_factor
            if not two_factor.is_enabled:
                raise serializers.ValidationError('Two-Factor Authentication is not currently enabled.')
        except:
            raise serializers.ValidationError('Two-Factor Authentication is not currently enabled.')
        
        if totp_code:
            # Verify TOTP code
            secret_key = two_factor.get_secret_key()
            if not secret_key:
                raise serializers.ValidationError('2FA configuration error. Please contact support.')
            
            import pyotp
            totp = pyotp.TOTP(secret_key)
            if not totp.verify(totp_code, valid_window=1):
                raise serializers.ValidationError('Invalid TOTP code. Please check your authenticator app and try again.')
        
        elif backup_code:
            # Verify backup code
            backup_code_obj = None
            for bc in two_factor.backup_codes.filter(is_used=False):
                if bc.verify_code(backup_code):
                    backup_code_obj = bc
                    break
            
            if not backup_code_obj:
                raise serializers.ValidationError('Invalid or already used backup code.')
            
            attrs['backup_code_obj'] = backup_code_obj
        
        attrs['two_factor'] = two_factor
        return attrs


class TwoFactorStatusSerializer(serializers.Serializer):
    """Serializer for returning Two-Factor Authentication status."""
    
    is_enabled = serializers.BooleanField()
    backup_tokens_count = serializers.IntegerField()
    last_used_at = serializers.DateTimeField(allow_null=True)
    
    def to_representation(self, instance):
        if not instance:
            return {
                'is_enabled': False,
                'backup_tokens_count': 0,
                'last_used_at': None
            }
        
        return {
            'is_enabled': instance.is_enabled,
            'backup_tokens_count': instance.backup_tokens_count,
            'last_used_at': instance.last_used_at
        }