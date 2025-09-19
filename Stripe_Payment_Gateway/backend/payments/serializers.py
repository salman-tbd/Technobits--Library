"""
Serializers for payments app.
"""

from rest_framework import serializers
from decimal import Decimal
from django.conf import settings
from core.utils import validate_amount, validate_currency, format_currency
from .models import PaymentIntent, CheckoutSession, Payment, Refund, PaymentMethod, PaymentEvent


class PaymentIntentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating Payment Intents.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, allow_null=True)
    automatic_payment_methods = serializers.BooleanField(default=True)
    capture_method = serializers.ChoiceField(
        choices=['automatic', 'manual'],
        default='automatic'
    )
    confirmation_method = serializers.ChoiceField(
        choices=['automatic', 'manual'],
        default='automatic'
    )
    
    def validate_amount(self, value):
        """Validate payment amount."""
        currency = self.initial_data.get('currency', 'USD')
        is_valid, error_message = validate_amount(value, currency)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value
    
    def validate_currency(self, value):
        """Validate currency code."""
        is_valid, error_message = validate_currency(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value.upper()


class CheckoutSessionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating Checkout Sessions.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)
    metadata = serializers.JSONField(required=False, allow_null=True)
    mode = serializers.ChoiceField(
        choices=['payment', 'setup', 'subscription'],
        default='payment'
    )
    
    def validate_amount(self, value):
        """Validate payment amount."""
        currency = self.initial_data.get('currency', 'USD')
        is_valid, error_message = validate_amount(value, currency)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value
    
    def validate_currency(self, value):
        """Validate currency code."""
        is_valid, error_message = validate_currency(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value.upper()


class PaymentIntentSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentIntent model.
    """
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_refundable = serializers.BooleanField(read_only=True)
    refunded_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = PaymentIntent
        fields = [
            'id', 'stripe_payment_intent_id', 'amount', 'amount_display',
            'currency', 'status', 'status_display', 'description',
            'payment_method_type', 'client_secret', 'is_successful',
            'is_refundable', 'refunded_amount', 'metadata',
            'created_at', 'updated_at', 'succeeded_at', 'canceled_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_intent_id', 'client_secret',
            'created_at', 'updated_at', 'succeeded_at', 'canceled_at'
        ]
    
    def get_amount_display(self, obj):
        """Get formatted amount for display."""
        return format_currency(obj.amount, obj.currency)


class CheckoutSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for CheckoutSession model.
    """
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'stripe_session_id', 'mode', 'status', 'status_display',
            'amount_total', 'amount_display', 'currency', 'checkout_url',
            'success_url', 'cancel_url', 'description', 'is_expired',
            'metadata', 'created_at', 'updated_at', 'expires_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'stripe_session_id', 'checkout_url',
            'created_at', 'updated_at', 'expires_at', 'completed_at'
        ]
    
    def get_amount_display(self, obj):
        """Get formatted amount for display."""
        if obj.amount_total:
            return format_currency(obj.amount_total, obj.currency)
        return None


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    """
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.SerializerMethodField()
    is_successful = serializers.BooleanField(read_only=True)
    is_refundable = serializers.BooleanField(read_only=True)
    refunded_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    refundable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_refunded = serializers.BooleanField(read_only=True)
    net_amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'reference_id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'amount', 'amount_display', 'currency', 'status', 'status_display',
            'description', 'payment_method_type', 'payment_method_display',
            'payment_method_details', 'application_fee', 'processing_fee',
            'tax_amount', 'net_amount', 'net_amount_display', 'receipt_email',
            'receipt_number', 'receipt_url', 'billing_details', 'is_successful',
            'is_refundable', 'refunded_amount', 'refundable_amount',
            'is_fully_refunded', 'failure_code', 'failure_message',
            'metadata', 'created_at', 'updated_at', 'succeeded_at',
            'failed_at', 'canceled_at'
        ]
        read_only_fields = [
            'id', 'reference_id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'payment_method_details', 'application_fee', 'processing_fee',
            'tax_amount', 'net_amount', 'receipt_number', 'receipt_url',
            'billing_details', 'failure_code', 'failure_message',
            'created_at', 'updated_at', 'succeeded_at', 'failed_at', 'canceled_at'
        ]
    
    def get_amount_display(self, obj):
        """Get formatted amount for display."""
        return format_currency(obj.amount, obj.currency)
    
    def get_net_amount_display(self, obj):
        """Get formatted net amount for display."""
        return format_currency(obj.net_amount, obj.currency)
    
    def get_payment_method_display(self, obj):
        """Get payment method display name."""
        if obj.payment_method_type == 'card' and obj.payment_method_details:
            details = obj.payment_method_details
            brand = details.get('brand', '').upper()
            last4 = details.get('last4', '')
            if brand and last4:
                return f"{brand} •••• {last4}"
        
        return obj.get_payment_method_type_display()


class RefundCreateSerializer(serializers.Serializer):
    """
    Serializer for creating refunds.
    """
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    reason = serializers.ChoiceField(
        choices=Refund.REASON_CHOICES,
        default='requested_by_customer'
    )
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        self.payment = kwargs.pop('payment', None)
        super().__init__(*args, **kwargs)
    
    def validate_amount(self, value):
        """Validate refund amount."""
        if value is not None and self.payment:
            if value <= 0:
                raise serializers.ValidationError("Refund amount must be greater than 0.")
            
            if value > self.payment.refundable_amount:
                raise serializers.ValidationError(
                    f"Refund amount cannot exceed refundable amount of "
                    f"{format_currency(self.payment.refundable_amount, self.payment.currency)}."
                )
        
        return value


class RefundSerializer(serializers.ModelSerializer):
    """
    Serializer for Refund model.
    """
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    payment_reference = serializers.CharField(source='payment.reference_id', read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'stripe_refund_id', 'payment_reference', 'amount',
            'amount_display', 'currency', 'reason', 'reason_display',
            'status', 'status_display', 'description', 'receipt_number',
            'failure_reason', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_refund_id', 'receipt_number', 'failure_reason',
            'created_at', 'updated_at'
        ]
    
    def get_amount_display(self, obj):
        """Get formatted amount for display."""
        return format_currency(obj.amount, obj.currency)


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentMethod model.
    """
    display_name = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'stripe_payment_method_id', 'type', 'type_display',
            'display_name', 'card_brand', 'card_last4', 'card_exp_month',
            'card_exp_year', 'card_funding', 'card_country', 'bank_name',
            'bank_last4', 'wallet_type', 'is_default', 'is_active',
            'is_expired', 'billing_details', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_method_id', 'card_brand', 'card_last4',
            'card_exp_month', 'card_exp_year', 'card_funding', 'card_country',
            'bank_name', 'bank_last4', 'wallet_type', 'billing_details',
            'created_at', 'updated_at'
        ]


class PaymentEventSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentEvent model.
    """
    payment_reference = serializers.CharField(
        source='payment.reference_id', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = PaymentEvent
        fields = [
            'id', 'stripe_event_id', 'event_type', 'payment_reference',
            'processed', 'processing_error', 'created_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'stripe_event_id', 'event_type', 'processed',
            'processing_error', 'created_at', 'processed_at'
        ]


class PaymentStatsSerializer(serializers.Serializer):
    """
    Serializer for payment statistics.
    """
    total_payments = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_amount_display = serializers.CharField()
    successful_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    successful_amount_display = serializers.CharField()
    total_refunds = serializers.IntegerField()
    total_refund_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_refund_amount_display = serializers.CharField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_payment_amount_display = serializers.CharField()
    currency_breakdown = serializers.DictField()
    payment_method_breakdown = serializers.DictField()
    monthly_stats = serializers.ListField()


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for payment lists.
    """
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'reference_id', 'amount', 'amount_display', 'currency',
            'status', 'status_display', 'description', 'payment_method_type',
            'payment_method_display', 'created_at', 'succeeded_at'
        ]
    
    def get_amount_display(self, obj):
        """Get formatted amount for display."""
        return format_currency(obj.amount, obj.currency)
    
    def get_payment_method_display(self, obj):
        """Get payment method display name."""
        if obj.payment_method_type == 'card' and obj.payment_method_details:
            details = obj.payment_method_details
            brand = details.get('brand', '').upper()
            last4 = details.get('last4', '')
            if brand and last4:
                return f"{brand} •••• {last4}"
        
        return obj.get_payment_method_type_display()


# Response serializers for API endpoints
class PaymentIntentResponseSerializer(serializers.Serializer):
    """
    Response serializer for Payment Intent creation.
    """
    success = serializers.BooleanField()
    data = PaymentIntentSerializer(required=False, allow_null=True)
    message = serializers.CharField()
    error_code = serializers.CharField(required=False, allow_null=True)


class CheckoutSessionResponseSerializer(serializers.Serializer):
    """
    Response serializer for Checkout Session creation.
    """
    success = serializers.BooleanField()
    data = serializers.DictField(required=False, allow_null=True)
    message = serializers.CharField()


class RefundResponseSerializer(serializers.Serializer):
    """
    Response serializer for refund operations.
    """
    success = serializers.BooleanField()
    data = RefundSerializer(required=False, allow_null=True)
    message = serializers.CharField()
    errors = serializers.DictField(required=False, allow_null=True)


