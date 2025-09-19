"""
Stripe service layer for payment processing.
"""

import stripe
import logging
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.utils import (
    generate_payment_reference, 
    convert_to_stripe_amount, 
    convert_stripe_amount,
    sanitize_metadata
)
from .models import PaymentIntent, CheckoutSession, Payment, Refund, PaymentMethod

User = get_user_model()
logger = logging.getLogger(__name__)


class StripeServiceError(Exception):
    """Custom exception for Stripe service errors."""
    pass


class StripeService:
    """
    Service class to handle all Stripe API interactions.
    """
    
    def __init__(self):
        """Initialize Stripe service with API key."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    def create_or_get_customer(self, user: User) -> str:
        """
        Create or retrieve Stripe customer for user.
        
        Args:
            user: User instance
            
        Returns:
            Stripe customer ID
        """
        try:
            # Check if user already has a Stripe customer
            if user.stripe_customer_id:
                try:
                    # Verify customer still exists in Stripe
                    stripe.Customer.retrieve(user.stripe_customer_id)
                    return user.stripe_customer_id
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist, create new one
                    logger.warning(f"Stripe customer {user.stripe_customer_id} not found, creating new one")
                    user.stripe_customer_id = None
            
            # Create new customer
            customer_data = {
                'email': user.email,
                'name': user.get_full_name(),
                'metadata': {
                    'user_id': str(user.id),
                    'username': user.username,
                }
            }
            
            # Add address if available
            if user.address_line1:
                customer_data['address'] = {
                    'line1': user.address_line1,
                    'line2': user.address_line2 or None,
                    'city': user.city,
                    'state': user.state,
                    'postal_code': user.postal_code,
                    'country': user.country,
                }
            
            # Add phone if available
            if user.phone_number:
                customer_data['phone'] = user.phone_number
            
            customer = stripe.Customer.create(**customer_data)
            
            # Save customer ID to user
            user.stripe_customer_id = customer.id
            user.save(update_fields=['stripe_customer_id'])
            
            logger.info(f"Created Stripe customer {customer.id} for user {user.email}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer for user {user.email}: {e}")
            raise StripeServiceError(f"Failed to create customer: {e}")
    
    def create_payment_intent(
        self,
        user: User,
        amount: Decimal,
        currency: str = 'USD',
        description: str = '',
        metadata: Optional[Dict[str, Any]] = None,
        automatic_payment_methods: bool = True,
        capture_method: str = 'automatic',
        confirmation_method: str = 'automatic'
    ) -> PaymentIntent:
        """
        Create a Stripe Payment Intent.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code
            description: Payment description
            metadata: Additional metadata
            automatic_payment_methods: Enable automatic payment methods
            capture_method: Payment capture method
            confirmation_method: Payment confirmation method
            
        Returns:
            PaymentIntent instance
        """
        try:
            # Get or create Stripe customer
            customer_id = self.create_or_get_customer(user)
            
            # Convert amount to Stripe format (cents)
            stripe_amount = convert_to_stripe_amount(amount, currency)
            
            # Prepare metadata
            payment_metadata = {
                'user_id': str(user.id),
                'user_email': user.email,
                'description': description,
            }
            if metadata:
                payment_metadata.update(sanitize_metadata(metadata))
            
            # Create Payment Intent in Stripe
            intent_data = {
                'amount': stripe_amount,
                'currency': currency.lower(),
                'customer': customer_id,
                'description': description,
                'metadata': payment_metadata,
                'capture_method': capture_method,
                'confirmation_method': confirmation_method,
            }
            
            # Add automatic payment methods if enabled
            if automatic_payment_methods:
                intent_data['automatic_payment_methods'] = {'enabled': True}
            
            # Add receipt email
            if user.email:
                intent_data['receipt_email'] = user.email
            
            stripe_intent = stripe.PaymentIntent.create(**intent_data)
            
            # Create local PaymentIntent record
            payment_intent = PaymentIntent.objects.create(
                stripe_payment_intent_id=stripe_intent.id,
                user=user,
                stripe_customer_id=customer_id,
                amount=amount,
                currency=currency.upper(),
                status=stripe_intent.status,
                description=description,
                metadata=payment_metadata,
                client_secret=stripe_intent.client_secret,
                capture_method=capture_method,
                confirmation_method=confirmation_method,
                receipt_email=user.email,
            )
            
            logger.info(f"Created PaymentIntent {stripe_intent.id} for user {user.email}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating PaymentIntent for user {user.email}: {e}")
            raise StripeServiceError(f"Failed to create payment intent: {e}")
    
    def create_checkout_session(
        self,
        user: Optional[User],
        amount: Decimal,
        currency: str = 'USD',
        description: str = '',
        success_url: str = None,
        cancel_url: str = None,
        metadata: Optional[Dict[str, Any]] = None,
        mode: str = 'payment'
    ) -> CheckoutSession:
        """
        Create a Stripe Checkout Session.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code
            description: Payment description
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            metadata: Additional metadata
            mode: Checkout mode
            
        Returns:
            CheckoutSession instance
        """
        try:
            # Get or create Stripe customer (handle anonymous users)
            customer_id = self.create_or_get_customer(user) if user else None
            
            # Convert amount to Stripe format
            stripe_amount = convert_to_stripe_amount(amount, currency)
            
            # Prepare URLs
            success_url = success_url or settings.PAYMENT_SUCCESS_URL
            cancel_url = cancel_url or settings.PAYMENT_CANCEL_URL
            
            # Prepare metadata
            session_metadata = {
                'description': description,
                'anonymous': 'true' if not user else 'false',
            }
            if user:
                session_metadata.update({
                    'user_id': str(user.id),
                    'user_email': user.email,
                })
            if metadata:
                session_metadata.update(sanitize_metadata(metadata))
            
            # Create checkout session
            session_data = {
                'mode': mode,
                'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': cancel_url,
                'metadata': session_metadata,
            }
            
            # Add customer only if we have one
            if customer_id:
                session_data['customer'] = customer_id
            
            session_data['line_items'] = [{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': description or 'Payment',
                    },
                    'unit_amount': stripe_amount,
                },
                'quantity': 1,
            }]
            
            # Add payment intent data
            session_data['payment_intent_data'] = {
                'metadata': session_metadata,
            }
            
            # Add receipt email only if user exists
            if user and user.email:
                session_data['payment_intent_data']['receipt_email'] = user.email
            
            # Add other session configuration
            session_data.update({
                'billing_address_collection': 'auto',
                'phone_number_collection': {
                    'enabled': True,
                },
                'expires_at': int((timezone.now() + timezone.timedelta(hours=24)).timestamp()),
            })
            
            # Add customer update only if we have a customer
            if customer_id:
                session_data['customer_update'] = {
                    'address': 'auto',
                    'name': 'auto',
                }
            
            stripe_session = stripe.checkout.Session.create(**session_data)
            
            # Create local CheckoutSession record
            checkout_session = CheckoutSession.objects.create(
                stripe_session_id=stripe_session.id,
                user=user,
                stripe_customer_id=customer_id,
                mode=mode,
                amount_total=amount,
                currency=currency.upper(),
                success_url=success_url,
                cancel_url=cancel_url,
                checkout_url=stripe_session.url,
                description=description,
                metadata=session_metadata,
                customer_email=user.email,
                expires_at=timezone.datetime.fromtimestamp(
                    stripe_session.expires_at, 
                    tz=timezone.get_current_timezone()
                ),
            )
            
            logger.info(f"Created CheckoutSession {stripe_session.id} for user {user.email}")
            return checkout_session
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating CheckoutSession for user {user.email}: {e}")
            raise StripeServiceError(f"Failed to create checkout session: {e}")
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve Payment Intent from Stripe.
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            Payment Intent data
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving PaymentIntent {payment_intent_id}: {e}")
            raise StripeServiceError(f"Failed to retrieve payment intent: {e}")
    
    def retrieve_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve Checkout Session from Stripe.
        
        Args:
            session_id: Stripe Session ID
            
        Returns:
            Session data
        """
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving CheckoutSession {session_id}: {e}")
            raise StripeServiceError(f"Failed to retrieve checkout session: {e}")
    
    def create_refund(
        self,
        payment: Payment,
        amount: Optional[Decimal] = None,
        reason: str = 'requested_by_customer',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Refund:
        """
        Create a refund for a payment.
        
        Args:
            payment: Payment to refund
            amount: Refund amount (None for full refund)
            reason: Refund reason
            metadata: Additional metadata
            
        Returns:
            Refund instance
        """
        try:
            # Determine refund amount
            refund_amount = amount or payment.refundable_amount
            
            if refund_amount <= 0:
                raise StripeServiceError("Invalid refund amount")
            
            if refund_amount > payment.refundable_amount:
                raise StripeServiceError("Refund amount exceeds refundable amount")
            
            # Convert to Stripe format
            stripe_amount = convert_to_stripe_amount(refund_amount, payment.currency)
            
            # Prepare metadata
            refund_metadata = {
                'payment_id': str(payment.id),
                'user_id': str(payment.user.id),
                'original_amount': str(payment.amount),
                'refund_amount': str(refund_amount),
            }
            if metadata:
                refund_metadata.update(sanitize_metadata(metadata))
            
            # Create refund in Stripe
            refund_data = {
                'charge': payment.stripe_charge_id,
                'amount': stripe_amount,
                'reason': reason,
                'metadata': refund_metadata,
            }
            
            stripe_refund = stripe.Refund.create(**refund_data)
            
            # Create local Refund record
            refund = Refund.objects.create(
                stripe_refund_id=stripe_refund.id,
                payment=payment,
                amount=refund_amount,
                currency=payment.currency,
                reason=reason,
                status=stripe_refund.status,
                metadata=refund_metadata,
            )
            
            logger.info(f"Created refund {stripe_refund.id} for payment {payment.reference_id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating refund for payment {payment.reference_id}: {e}")
            raise StripeServiceError(f"Failed to create refund: {e}")
    
    def sync_payment_intent(self, payment_intent: PaymentIntent) -> PaymentIntent:
        """
        Sync local PaymentIntent with Stripe data.
        
        Args:
            payment_intent: Local PaymentIntent instance
            
        Returns:
            Updated PaymentIntent instance
        """
        try:
            stripe_intent = self.retrieve_payment_intent(payment_intent.stripe_payment_intent_id)
            
            # Update local record
            payment_intent.status = stripe_intent.status
            payment_intent.payment_method_id = stripe_intent.payment_method or ''
            payment_intent.last_payment_error = stripe_intent.last_payment_error
            
            # Update timestamps based on status
            if stripe_intent.status == 'succeeded' and not payment_intent.succeeded_at:
                payment_intent.succeeded_at = timezone.now()
            elif stripe_intent.status == 'canceled' and not payment_intent.canceled_at:
                payment_intent.canceled_at = timezone.now()
            
            payment_intent.save()
            
            # Create Payment record if succeeded
            if stripe_intent.status == 'succeeded' and not hasattr(payment_intent, 'payment'):
                self._create_payment_from_intent(payment_intent, stripe_intent)
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Error syncing PaymentIntent {payment_intent.stripe_payment_intent_id}: {e}")
            raise StripeServiceError(f"Failed to sync payment intent: {e}")
    
    def _create_payment_from_intent(self, payment_intent: PaymentIntent, stripe_intent: Dict[str, Any]):
        """
        Create Payment record from successful PaymentIntent.
        
        Args:
            payment_intent: Local PaymentIntent instance
            stripe_intent: Stripe PaymentIntent data
        """
        try:
            # Get charge information
            charges = stripe_intent.get('charges', {}).get('data', [])
            charge = charges[0] if charges else {}
            
            # Extract payment method details
            payment_method_details = {}
            payment_method_type = 'other'
            
            if charge.get('payment_method_details'):
                pm_details = charge['payment_method_details']
                payment_method_type = pm_details.get('type', 'other')
                
                if payment_method_type == 'card':
                    card_info = pm_details.get('card', {})
                    payment_method_details = {
                        'brand': card_info.get('brand'),
                        'last4': card_info.get('last4'),
                        'exp_month': card_info.get('exp_month'),
                        'exp_year': card_info.get('exp_year'),
                        'funding': card_info.get('funding'),
                        'country': card_info.get('country'),
                    }
            
            # Calculate fees and net amount
            application_fee = Decimal('0.00')
            processing_fee = Decimal('0.00')
            
            if charge.get('balance_transaction'):
                # In a real implementation, you'd retrieve the balance transaction
                # For now, estimate processing fee (2.9% + $0.30 for cards)
                if payment_method_type == 'card':
                    processing_fee = (payment_intent.amount * Decimal('0.029')) + Decimal('0.30')
                    processing_fee = min(processing_fee, payment_intent.amount)
            
            net_amount = payment_intent.amount - application_fee - processing_fee
            
            # Create Payment record
            payment = Payment.objects.create(
                reference_id=generate_payment_reference(),
                user=payment_intent.user,
                payment_intent=payment_intent,
                stripe_payment_intent_id=payment_intent.stripe_payment_intent_id,
                stripe_customer_id=payment_intent.stripe_customer_id,
                stripe_charge_id=charge.get('id', ''),
                amount=payment_intent.amount,
                currency=payment_intent.currency,
                status='succeeded',
                description=payment_intent.description,
                payment_method_type=payment_method_type,
                payment_method_details=payment_method_details,
                application_fee=application_fee,
                processing_fee=processing_fee,
                net_amount=net_amount,
                receipt_email=payment_intent.receipt_email,
                receipt_url=charge.get('receipt_url', ''),
                billing_details=charge.get('billing_details', {}),
                metadata=payment_intent.metadata,
                succeeded_at=timezone.now(),
            )
            
            logger.info(f"Created Payment {payment.reference_id} from PaymentIntent {payment_intent.stripe_payment_intent_id}")
            
        except Exception as e:
            logger.error(f"Error creating Payment from PaymentIntent {payment_intent.stripe_payment_intent_id}: {e}")
    
    def list_customer_payment_methods(self, user: User, type: str = 'card') -> list:
        """
        List customer's payment methods from Stripe.
        
        Args:
            user: User instance
            type: Payment method type
            
        Returns:
            List of payment methods
        """
        try:
            if not user.stripe_customer_id:
                return []
            
            payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_customer_id,
                type=type,
            )
            
            return payment_methods.data
            
        except stripe.error.StripeError as e:
            logger.error(f"Error listing payment methods for user {user.email}: {e}")
            raise StripeServiceError(f"Failed to list payment methods: {e}")
    
    def detach_payment_method(self, payment_method_id: str):
        """
        Detach payment method from customer.
        
        Args:
            payment_method_id: Stripe Payment Method ID
        """
        try:
            stripe.PaymentMethod.detach(payment_method_id)
            logger.info(f"Detached payment method {payment_method_id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Error detaching payment method {payment_method_id}: {e}")
            raise StripeServiceError(f"Failed to detach payment method: {e}")
    
    def construct_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Construct and verify webhook event from Stripe.
        
        Args:
            payload: Raw request payload
            signature: Stripe signature header
            
        Returns:
            Verified event data
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise StripeServiceError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise StripeServiceError("Invalid signature")


# Global service instance
stripe_service = StripeService()
