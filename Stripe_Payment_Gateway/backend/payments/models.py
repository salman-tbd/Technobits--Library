"""
Simple Stripe Payment models.
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal


class StripeTransaction(models.Model):
    """
    Model to track Stripe payment transactions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    # Transaction details
    transaction_id = models.CharField(max_length=255, unique=True)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    
    # Payment info
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe response data
    stripe_response = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol."""
        return f"${self.amount}"