"""
Payment Serializers for API responses
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PaymentTransaction, PaymentWebhook, PaymentMethod


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for payment contexts"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    user = UserSerializer(read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'transaction_id',
            'user',
            'provider',
            'provider_display',
            'amount',
            'currency',
            'description',
            'status',
            'status_display',
            'provider_transaction_id',
            'provider_order_id',
            'provider_payment_id',
            'created_at',
            'updated_at',
            'completed_at',
            'is_completed',
            'is_failed',
            'can_be_refunded',
        ]
        read_only_fields = [
            'id',
            'transaction_id',
            'user',
            'provider_transaction_id',
            'provider_order_id',
            'provider_payment_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment transactions"""
    class Meta:
        model = PaymentTransaction
        fields = [
            'provider',
            'amount',
            'currency',
            'description',
        ]
        
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer for payment webhooks"""
    transaction = PaymentTransactionSerializer(read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id',
            'provider',
            'provider_display',
            'webhook_id',
            'event_type',
            'processed',
            'processed_at',
            'processing_result',
            'transaction',
            'received_at',
        ]
        read_only_fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods"""
    user = UserSerializer(read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'user',
            'provider',
            'provider_display',
            'method_type',
            'last_four',
            'brand',
            'is_active',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]


class GooglePayProcessSerializer(serializers.Serializer):
    """Serializer for Google Pay payment processing requests"""
    token = serializers.CharField(max_length=10000, help_text="Google Pay payment token")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=3, default='INR')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_currency(self, value):
        """Validate currency code"""
        allowed_currencies = ['INR', 'USD', 'EUR', 'GBP']
        if value.upper() not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(allowed_currencies)}")
        return value.upper()


class PayPalCreateOrderSerializer(serializers.Serializer):
    """Serializer for PayPal order creation requests"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_currency(self, value):
        """Validate currency code"""
        allowed_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        if value.upper() not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(allowed_currencies)}")
        return value.upper()


class PayPalCaptureOrderSerializer(serializers.Serializer):
    """Serializer for PayPal order capture requests"""
    order_id = serializers.CharField(max_length=255, help_text="PayPal order ID to capture")


class PaymentAnalyticsSerializer(serializers.Serializer):
    """Serializer for payment analytics data"""
    total_transactions = serializers.IntegerField()
    completed_transactions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    total_amount = serializers.FloatField()
    provider_breakdown = serializers.DictField()
    recent_transactions = serializers.ListField(child=serializers.DictField())


class TransactionStatsSerializer(serializers.Serializer):
    """Serializer for transaction statistics"""
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    success_rate = serializers.FloatField()
    
    
class PaymentResponseSerializer(serializers.Serializer):
    """Generic serializer for payment API responses"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    transaction_id = serializers.CharField(required=False)
    order_id = serializers.CharField(required=False)
    amount = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
