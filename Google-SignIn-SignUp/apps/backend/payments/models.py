"""
Payment Models for Unified Payment Processing
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PaymentProvider(models.TextChoices):
    """Payment provider choices"""
    GOOGLE_PAY = 'google_pay', 'Google Pay'
    PAYPAL = 'paypal', 'PayPal'


class TransactionStatus(models.TextChoices):
    """Transaction status choices"""
    CREATED = 'created', 'Created'
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class PaymentTransaction(models.Model):
    """
    Unified payment transaction model for all payment providers
    """
    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True)
    
    # User and provider info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.CREATED)
    
    # Provider-specific data
    provider_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    provider_order_id = models.CharField(max_length=255, blank=True, null=True)  # For PayPal Order ID
    provider_payment_id = models.CharField(max_length=255, blank=True, null=True)  # For PayPal Payment ID
    provider_token = models.TextField(blank=True)  # For Google Pay tokens
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'provider']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_transaction_id']),
            models.Index(fields=['provider_order_id']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.provider} - {self.amount} {self.currency} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-generate transaction ID if not provided
        if not self.transaction_id:
            self.transaction_id = f"{self.provider}_{timezone.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Set completed_at when status changes to completed
        if self.status == TransactionStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
            
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_failed(self):
        return self.status == TransactionStatus.FAILED
    
    @property
    def can_be_refunded(self):
        return self.status == TransactionStatus.COMPLETED


class PaymentWebhook(models.Model):
    """
    Store webhook events from payment providers
    """
    # Provider info
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    webhook_id = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Event details
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    
    # Processing info
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_result = models.TextField(blank=True)
    
    # Related transaction
    transaction = models.ForeignKey(
        PaymentTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhooks'
    )
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['provider', 'webhook_id']),
            models.Index(fields=['processed', 'received_at']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.provider} - {self.event_type} - {self.webhook_id}"
    
    def mark_processed(self, result=""):
        """Mark webhook as processed"""
        self.processed = True
        self.processed_at = timezone.now()
        self.processing_result = result
        self.save()


class PaymentMethod(models.Model):
    """
    Store user payment methods (optional - for future use)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    
    # Method details
    method_type = models.CharField(max_length=50)  # 'card', 'paypal_account', etc.
    last_four = models.CharField(max_length=4, blank=True)  # Last 4 digits of card
    brand = models.CharField(max_length=20, blank=True)  # VISA, MASTERCARD, etc.
    
    # Provider-specific data
    provider_method_id = models.CharField(max_length=255, blank=True)
    provider_data = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'provider_method_id']

    def __str__(self):
        return f"{self.user.email} - {self.provider} - {self.method_type}"
