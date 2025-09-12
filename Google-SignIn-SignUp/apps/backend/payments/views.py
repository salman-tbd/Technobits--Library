"""
Payment API Views for Google Pay and PayPal Integration
"""
import json
import logging
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import PaymentTransaction, PaymentProvider, TransactionStatus, PaymentWebhook
from .services import GooglePayService, PayPalService, UnifiedPaymentService, PaymentServiceError
from .serializers import PaymentTransactionSerializer

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


class GooglePayProcessView(APIView):
    """
    API endpoint to process Google Pay payments
    
    POST /api/payments/google-pay/process/
    {
        "token": "google_pay_token",
        "amount": "10.00",
        "currency": "INR",
        "description": "Payment description"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data from request
            token = request.data.get('token')
            amount = request.data.get('amount')
            currency = request.data.get('currency', 'INR')
            description = request.data.get('description', '')

            # Validate required fields
            if not token:
                return Response(
                    {'error': 'Payment token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not amount:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate amount
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError("Amount must be positive")
            except (InvalidOperation, ValueError) as e:
                return Response(
                    {'error': f'Invalid amount: {e}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process payment
            google_pay_service = GooglePayService()
            transaction = google_pay_service.process_payment(
                user=request.user,
                amount=str(amount_decimal),
                currency=currency,
                token=token,
                description=description,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )

            logger.info(f"Google Pay payment processed - Transaction: {transaction.transaction_id}, Status: {transaction.status}")

            # Serialize response
            serializer = PaymentTransactionSerializer(transaction)
            
            if transaction.is_completed:
                return Response({
                    'status': 'success',
                    'message': 'Payment processed successfully',
                    'transaction': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Payment processing failed',
                    'transaction': serializer.data
                }, status=status.HTTP_400_BAD_REQUEST)

        except PaymentServiceError as e:
            logger.error(f"Google Pay service error: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in Google Pay processing: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayPalCreateOrderView(APIView):
    """
    API endpoint to create PayPal orders
    
    POST /api/payments/paypal/create-order/
    {
        "amount": "10.00",
        "currency": "USD",
        "description": "Payment description"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data from request
            amount = request.data.get('amount')
            currency = request.data.get('currency', 'USD')
            description = request.data.get('description', '')

            # Validate required fields
            if not amount:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate amount
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError("Amount must be positive")
            except (InvalidOperation, ValueError) as e:
                return Response(
                    {'error': f'Invalid amount: {e}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create PayPal order
            paypal_service = PayPalService()
            order_id, transaction = paypal_service.create_order(
                user=request.user,
                amount=str(amount_decimal),
                currency=currency,
                description=description,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )

            logger.info(f"PayPal order created - Order ID: {order_id}, Transaction: {transaction.transaction_id}")

            return Response({
                'success': True,
                'order_id': order_id,
                'transaction_id': transaction.transaction_id,
                'amount': str(amount_decimal),
                'currency': currency
            }, status=status.HTTP_201_CREATED)

        except PaymentServiceError as e:
            logger.error(f"PayPal service error in create order: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in PayPal create order: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PayPalCaptureOrderView(APIView):
    """
    API endpoint to capture PayPal orders
    
    POST /api/payments/paypal/capture-order/
    {
        "order_id": "PAYPAL_ORDER_ID"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order_id = request.data.get('order_id')

            if not order_id:
                return Response(
                    {'error': 'order_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Capture PayPal order
            paypal_service = PayPalService()
            success, paypal_response, transaction = paypal_service.capture_order(order_id)

            logger.info(f"PayPal order capture attempt - Order ID: {order_id}, Success: {success}")

            # Serialize response
            serializer = PaymentTransactionSerializer(transaction)

            if success:
                return Response({
                    'success': True,
                    'message': 'Payment captured successfully',
                    'transaction_id': transaction.transaction_id,
                    'transaction': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to capture payment',
                    'transaction': serializer.data
                }, status=status.HTTP_400_BAD_REQUEST)

        except PaymentServiceError as e:
            logger.error(f"PayPal service error in capture order: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in PayPal capture order: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(APIView):
    """
    API endpoint to receive PayPal webhook notifications
    
    POST /api/payments/paypal/webhook/
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
                logger.error("Invalid JSON in PayPal webhook request")
                return Response(
                    {'error': 'Invalid JSON'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract webhook event details
            event_id = webhook_data.get('id')
            event_type = webhook_data.get('event_type')
            resource = webhook_data.get('resource', {})

            if not event_id or not event_type:
                logger.error("Missing required webhook fields")
                return Response(
                    {'error': 'Missing required fields'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if we've already processed this event
            if PaymentWebhook.objects.filter(
                provider=PaymentProvider.PAYPAL,
                webhook_id=event_id
            ).exists():
                logger.info(f"PayPal webhook event {event_id} already processed")
                return Response({'success': True}, status=status.HTTP_200_OK)

            # Save webhook event
            webhook_event = PaymentWebhook.objects.create(
                provider=PaymentProvider.PAYPAL,
                webhook_id=event_id,
                event_type=event_type,
                event_data=webhook_data
            )

            # Process specific event types
            processing_result = ""
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                processing_result = self._handle_payment_completed(webhook_event, resource)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                processing_result = self._handle_payment_denied(webhook_event, resource)
            else:
                processing_result = f"Event type {event_type} not specifically handled"

            # Mark as processed
            webhook_event.mark_processed(processing_result)

            logger.info(f"Successfully processed PayPal webhook event {event_id}")
            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_payment_completed(self, webhook_event, resource):
        """Handle PAYMENT.CAPTURE.COMPLETED webhook"""
        try:
            # Look for the order ID in the resource or supplementary_data
            order_id = None
            
            if 'supplementary_data' in resource:
                related_ids = resource['supplementary_data'].get('related_ids', {})
                order_id = related_ids.get('order_id')
            
            payment_id = resource.get('id')
            
            if order_id:
                try:
                    transaction = PaymentTransaction.objects.get(
                        provider=PaymentProvider.PAYPAL,
                        provider_order_id=order_id
                    )
                    webhook_event.transaction = transaction
                    webhook_event.save()
                    
                    # Update transaction status if not already completed
                    if transaction.status != TransactionStatus.COMPLETED:
                        transaction.status = TransactionStatus.COMPLETED
                        transaction.completed_at = timezone.now()
                        transaction.provider_payment_id = payment_id
                        transaction.save()
                        return f"Updated transaction {transaction.transaction_id} status to COMPLETED"
                    else:
                        return f"Transaction {transaction.transaction_id} already completed"
                        
                except PaymentTransaction.DoesNotExist:
                    return f"Transaction not found for order {order_id}"
            else:
                return "No order ID found in webhook data"
                
        except Exception as e:
            logger.error(f"Error handling payment completed webhook: {e}")
            return f"Error: {str(e)}"

    def _handle_payment_denied(self, webhook_event, resource):
        """Handle PAYMENT.CAPTURE.DENIED webhook"""
        try:
            order_id = None
            
            if 'supplementary_data' in resource:
                related_ids = resource['supplementary_data'].get('related_ids', {})
                order_id = related_ids.get('order_id')
            
            if order_id:
                try:
                    transaction = PaymentTransaction.objects.get(
                        provider=PaymentProvider.PAYPAL,
                        provider_order_id=order_id
                    )
                    webhook_event.transaction = transaction
                    webhook_event.save()
                    
                    transaction.status = TransactionStatus.FAILED
                    transaction.save()
                    return f"Updated transaction {transaction.transaction_id} status to FAILED"
                    
                except PaymentTransaction.DoesNotExist:
                    return f"Transaction not found for order {order_id}"
            else:
                return "No order ID found in webhook data"
                    
        except Exception as e:
            logger.error(f"Error handling payment denied webhook: {e}")
            return f"Error: {str(e)}"


class TransactionListView(APIView):
    """
    API endpoint to get user's transactions
    
    GET /api/payments/transactions/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(limit, 100)  # Cap at 100 transactions
            
            unified_service = UnifiedPaymentService()
            transactions = unified_service.get_user_transactions(request.user, limit)
            
            serializer = PaymentTransactionSerializer(transactions, many=True)
            
            return Response({
                'success': True,
                'transactions': serializer.data,
                'count': len(serializer.data)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching user transactions: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentAnalyticsView(APIView):
    """
    API endpoint to get payment analytics
    
    GET /api/payments/analytics/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Check if user wants global analytics (for admin) or just their own
            include_all = request.query_params.get('all', 'false').lower() == 'true'
            user = None if (include_all and request.user.is_staff) else request.user
            
            unified_service = UnifiedPaymentService()
            analytics_data = unified_service.get_analytics_data(user)
            
            return Response({
                'success': True,
                'analytics': analytics_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching payment analytics: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionDetailView(APIView):
    """
    API endpoint to get transaction details
    
    GET /api/payments/transactions/{transaction_id}/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            transaction = PaymentTransaction.objects.get(
                transaction_id=transaction_id,
                user=request.user
            )
            
            serializer = PaymentTransactionSerializer(transaction)
            
            return Response({
                'success': True,
                'transaction': serializer.data
            }, status=status.HTTP_200_OK)

        except PaymentTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching transaction details: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
