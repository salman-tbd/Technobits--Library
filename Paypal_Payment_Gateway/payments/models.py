"""
PayPal Payment Models
"""
from django.db import models
from django.contrib.auth.models import User
import json


class PayPalTransaction(models.Model):
    """
    Model to store PayPal transaction details
    """
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('SAVED', 'Saved'),
        ('APPROVED', 'Approved'),
        ('VOIDED', 'Voided'),
        ('COMPLETED', 'Completed'),
        ('PAYER_ACTION_REQUIRED', 'Payer Action Required'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]

    # PayPal order/payment IDs
    paypal_order_id = models.CharField(max_length=255, unique=True)
    paypal_payment_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CREATED')
    
    # User and metadata
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # PayPal response data (stored as JSON)
    paypal_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paypal_order_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"PayPal Transaction {self.paypal_order_id} - {self.amount} {self.currency}"

    def get_paypal_response_formatted(self):
        """Return formatted PayPal response for admin display"""
        return json.dumps(self.paypal_response, indent=2)


class PayPalWebhookEvent(models.Model):
    """
    Model to store PayPal webhook events for auditing and processing
    """
    EVENT_TYPES = [
        ('PAYMENT.CAPTURE.COMPLETED', 'Payment Capture Completed'),
        ('PAYMENT.CAPTURE.DENIED', 'Payment Capture Denied'),
        ('PAYMENT.CAPTURE.PENDING', 'Payment Capture Pending'),
        ('PAYMENT.CAPTURE.REFUNDED', 'Payment Capture Refunded'),
        ('PAYMENT.CAPTURE.REVERSED', 'Payment Capture Reversed'),
    ]

    # Webhook event details
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=255)  # Payment ID, Order ID, etc.
    
    # Raw webhook data
    webhook_data = models.JSONField()
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Related transaction
    transaction = models.ForeignKey(
        PayPalTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhook_events'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['processed']),
        ]

    def __str__(self):
        return f"Webhook Event {self.event_id} - {self.event_type}"
