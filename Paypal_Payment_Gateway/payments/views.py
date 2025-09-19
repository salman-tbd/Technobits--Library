"""
PayPal Payment API Views
"""
import json
import logging
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import PayPalTransaction, PayPalWebhookEvent
from .services import PayPalService, PayPalAPIError

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    """
    API endpoint to create a PayPal order
    
    POST /api/paypal/create-order/
    {
        "amount": "10.00",
        "currency": "USD",
        "description": "Product purchase"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Validate request data
            amount_str = request.data.get('amount')
            currency = request.data.get('currency', 'USD')
            description = request.data.get('description', '')

            if not amount_str:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate amount
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except (InvalidOperation, ValueError) as e:
                return Response(
                    {'error': f'Invalid amount: {e}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create PayPal order
            paypal_service = PayPalService()
            order_id, paypal_response = paypal_service.create_order(
                amount=str(amount),
                currency=currency,
                description=description
            )

            # Save transaction to database
            transaction = PayPalTransaction.objects.create(
                paypal_order_id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                paypal_response=paypal_response,
                user=request.user if request.user.is_authenticated else None
            )

            logger.info(f"Created PayPal order {order_id} for amount {amount} {currency}")

            return Response({
                'success': True,
                'order_id': order_id,
                'amount': str(amount),
                'currency': currency
            }, status=status.HTTP_201_CREATED)

        except PayPalAPIError as e:
            logger.error(f"PayPal API error in create order: {e}")
            return Response(
                {'error': f'PayPal API error: {e}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create order: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CaptureOrderView(APIView):
    """
    API endpoint to capture a PayPal order after approval
    
    POST /api/paypal/capture-order/
    {
        "order_id": "PAYPAL_ORDER_ID"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            order_id = request.data.get('order_id')

            if not order_id:
                return Response(
                    {'error': 'order_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Find the transaction in our database
            try:
                transaction = PayPalTransaction.objects.get(paypal_order_id=order_id)
            except PayPalTransaction.DoesNotExist:
                return Response(
                    {'error': 'Transaction not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if already captured
            if transaction.status == 'COMPLETED':
                return Response({
                    'success': True,
                    'message': 'Order already captured',
                    'transaction_id': transaction.id,
                    'paypal_order_id': order_id
                })

            # Capture the PayPal order
            paypal_service = PayPalService()
            success, paypal_response = paypal_service.capture_order(order_id)

            # Update transaction
            transaction.paypal_response = paypal_response
            transaction.status = 'COMPLETED' if success else 'FAILED'
            
            if success:
                transaction.completed_at = timezone.now()
                # Extract payment ID from response
                if 'purchase_units' in paypal_response:
                    for unit in paypal_response['purchase_units']:
                        if 'payments' in unit and 'captures' in unit['payments']:
                            for capture in unit['payments']['captures']:
                                transaction.paypal_payment_id = capture.get('id')
                                break

            transaction.save()

            if success:
                logger.info(f"Successfully captured PayPal order {order_id}")
                return Response({
                    'success': True,
                    'message': 'Payment captured successfully',
                    'transaction_id': transaction.id,
                    'paypal_order_id': order_id,
                    'amount': str(transaction.amount),
                    'currency': transaction.currency
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Failed to capture PayPal order {order_id}")
                return Response(
                    {'error': 'Failed to capture payment'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except PayPalAPIError as e:
            logger.error(f"PayPal API error in capture order: {e}")
            return Response(
                {'error': f'PayPal API error: {e}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in capture order: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(APIView):
    """
    API endpoint to receive PayPal webhook notifications
    
    POST /api/paypal/webhook/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Get raw body for signature verification
            raw_body = request.body.decode('utf-8')
            
            # Parse webhook data
            try:
                webhook_data = json.loads(raw_body)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in webhook request")
                return Response(
                    {'error': 'Invalid JSON'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract webhook event details
            event_id = webhook_data.get('id')
            event_type = webhook_data.get('event_type')
            resource = webhook_data.get('resource', {})
            resource_id = resource.get('id', '')

            if not event_id or not event_type:
                logger.error("Missing required webhook fields")
                return Response(
                    {'error': 'Missing required fields'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if we've already processed this event
            if PayPalWebhookEvent.objects.filter(event_id=event_id).exists():
                logger.info(f"Webhook event {event_id} already processed")
                return Response({'success': True}, status=status.HTTP_200_OK)

            # Optional: Verify webhook signature
            # paypal_service = PayPalService()
            # if not paypal_service.verify_webhook_signature(request.headers, raw_body, settings.PAYPAL_WEBHOOK_ID):
            #     logger.error("Invalid webhook signature")
            #     return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

            # Save webhook event
            webhook_event = PayPalWebhookEvent.objects.create(
                event_id=event_id,
                event_type=event_type,
                resource_id=resource_id,
                webhook_data=webhook_data
            )

            # Process specific event types
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                self._handle_payment_completed(webhook_event, resource)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                self._handle_payment_denied(webhook_event, resource)

            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            logger.info(f"Successfully processed webhook event {event_id}")
            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_payment_completed(self, webhook_event, resource):
        """Handle PAYMENT.CAPTURE.COMPLETED webhook"""
        try:
            # Find the related transaction
            # Look for the order ID in the resource or supplementary_data
            order_id = None
            
            # PayPal sometimes includes the order ID in different places
            if 'supplementary_data' in resource:
                related_ids = resource['supplementary_data'].get('related_ids', {})
                order_id = related_ids.get('order_id')
            
            # Alternative: find by payment ID
            payment_id = resource.get('id')
            
            if order_id:
                try:
                    transaction = PayPalTransaction.objects.get(paypal_order_id=order_id)
                    webhook_event.transaction = transaction
                    webhook_event.save()
                    
                    # Update transaction status if not already completed
                    if transaction.status != 'COMPLETED':
                        transaction.status = 'COMPLETED'
                        transaction.completed_at = timezone.now()
                        transaction.paypal_payment_id = payment_id
                        transaction.save()
                        logger.info(f"Updated transaction {transaction.id} status to COMPLETED")
                        
                except PayPalTransaction.DoesNotExist:
                    logger.warning(f"Transaction not found for order {order_id}")
            else:
                logger.warning("No order ID found in webhook data")
                
        except Exception as e:
            logger.error(f"Error handling payment completed webhook: {e}")

    def _handle_payment_denied(self, webhook_event, resource):
        """Handle PAYMENT.CAPTURE.DENIED webhook"""
        try:
            # Similar logic to payment completed but set status to FAILED
            order_id = None
            
            if 'supplementary_data' in resource:
                related_ids = resource['supplementary_data'].get('related_ids', {})
                order_id = related_ids.get('order_id')
            
            if order_id:
                try:
                    transaction = PayPalTransaction.objects.get(paypal_order_id=order_id)
                    webhook_event.transaction = transaction
                    webhook_event.save()
                    
                    transaction.status = 'FAILED'
                    transaction.save()
                    logger.info(f"Updated transaction {transaction.id} status to FAILED")
                    
                except PayPalTransaction.DoesNotExist:
                    logger.warning(f"Transaction not found for order {order_id}")
                    
        except Exception as e:
            logger.error(f"Error handling payment denied webhook: {e}")


class TransactionStatusView(APIView):
    """
    API endpoint to check transaction status
    
    GET /api/paypal/transaction-status/{order_id}/
    """
    permission_classes = [AllowAny]

    def get(self, request, order_id):
        try:
            transaction = PayPalTransaction.objects.get(paypal_order_id=order_id)
            
            return Response({
                'success': True,
                'transaction_id': transaction.id,
                'paypal_order_id': transaction.paypal_order_id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'created_at': transaction.created_at,
                'completed_at': transaction.completed_at
            })
            
        except PayPalTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
