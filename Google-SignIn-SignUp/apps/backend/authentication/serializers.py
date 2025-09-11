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
