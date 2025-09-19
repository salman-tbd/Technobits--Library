"""
Signals for payments app.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import UserActivity
from .models import Payment, PaymentIntent, Refund
from core.utils import get_client_ip

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentIntent)
def payment_intent_created(sender, instance, created, **kwargs):
    """
    Handle PaymentIntent creation.
    """
    if created:
        logger.info(f"PaymentIntent created: {instance.stripe_payment_intent_id}")
        
        # Log user activity
        try:
            UserActivity.objects.create(
                user=instance.user,
                action='payment_created',
                description=f'Payment intent created for {instance.amount} {instance.currency}',
                metadata={
                    'payment_intent_id': instance.stripe_payment_intent_id,
                    'amount': str(instance.amount),
                    'currency': instance.currency,
                }
            )
        except Exception as e:
            logger.error(f"Failed to log payment intent creation activity: {e}")


@receiver(post_save, sender=Payment)
def payment_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle Payment creation and updates.
    """
    if created:
        logger.info(f"Payment created: {instance.reference_id}")
        
        # Log user activity for successful payment
        if instance.status == 'succeeded':
            try:
                UserActivity.objects.create(
                    user=instance.user,
                    action='payment_completed',
                    description=f'Payment completed for {instance.amount} {instance.currency}',
                    metadata={
                        'payment_id': str(instance.id),
                        'reference_id': instance.reference_id,
                        'amount': str(instance.amount),
                        'currency': instance.currency,
                        'payment_method': instance.payment_method_type,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to log payment completion activity: {e}")
        
        # Log user activity for failed payment
        elif instance.status == 'failed':
            try:
                UserActivity.objects.create(
                    user=instance.user,
                    action='payment_failed',
                    description=f'Payment failed for {instance.amount} {instance.currency}',
                    metadata={
                        'payment_id': str(instance.id),
                        'reference_id': instance.reference_id,
                        'amount': str(instance.amount),
                        'currency': instance.currency,
                        'failure_code': instance.failure_code,
                        'failure_message': instance.failure_message,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to log payment failure activity: {e}")
    
    else:
        # Handle status changes
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            new_status = instance.status
            
            logger.info(f"Payment {instance.reference_id} status changed from {old_status} to {new_status}")
            
            # Log status change activity
            try:
                UserActivity.objects.create(
                    user=instance.user,
                    action='payment_status_changed',
                    description=f'Payment status changed from {old_status} to {new_status}',
                    metadata={
                        'payment_id': str(instance.id),
                        'reference_id': instance.reference_id,
                        'old_status': old_status,
                        'new_status': new_status,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to log payment status change activity: {e}")


@receiver(post_save, sender=Refund)
def refund_created(sender, instance, created, **kwargs):
    """
    Handle Refund creation.
    """
    if created:
        logger.info(f"Refund created: {instance.stripe_refund_id}")
        
        # Log user activity
        try:
            UserActivity.objects.create(
                user=instance.payment.user,
                action='refund_requested',
                description=f'Refund requested for {instance.amount} {instance.currency}',
                metadata={
                    'refund_id': str(instance.id),
                    'stripe_refund_id': instance.stripe_refund_id,
                    'payment_reference': instance.payment.reference_id,
                    'amount': str(instance.amount),
                    'currency': instance.currency,
                    'reason': instance.reason,
                }
            )
        except Exception as e:
            logger.error(f"Failed to log refund creation activity: {e}")


@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    """
    Handle Payment pre-save operations.
    """
    # Calculate net amount if not set
    if instance.net_amount is None:
        application_fee = instance.application_fee or 0
        processing_fee = instance.processing_fee or 0
        tax_amount = instance.tax_amount or 0
        instance.net_amount = instance.amount - application_fee - processing_fee - tax_amount


# Add model tracking for change detection
def add_model_tracking():
    """
    Add change tracking to models.
    """
    try:
        from model_utils import FieldTracker
        
        # Add tracker to Payment model if not already present
        if not hasattr(Payment, 'tracker'):
            Payment.add_to_class('tracker', FieldTracker(fields=['status']))
            
    except ImportError:
        # model_utils not available, skip tracking
        logger.warning("model_utils not available, change tracking disabled")


# Initialize model tracking
add_model_tracking()


