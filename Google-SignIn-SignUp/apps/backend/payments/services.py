"""
Payment Services for Google Pay and PayPal Integration
"""
import json
import logging
import requests
import base64
from typing import Dict, Tuple, Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from .models import PaymentTransaction, TransactionStatus, PaymentProvider

logger = logging.getLogger(__name__)


class PaymentServiceError(Exception):
    """Custom exception for payment service errors"""
    pass


class GooglePayService:
    """Service class for Google Pay payment processing"""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'GOOGLE_PAY_MERCHANT_ID', '')
        self.environment = getattr(settings, 'GOOGLE_PAY_ENVIRONMENT', 'TEST')
    
    def process_payment(self, user: User, amount: str, currency: str, token: str, description: str = "", ip_address: str = None, user_agent: str = None) -> PaymentTransaction:
        """
        Process a Google Pay payment
        
        Args:
            user: Django User instance
            amount: Payment amount as string
            currency: Currency code (INR, USD, etc.)
            token: Google Pay payment token
            description: Payment description
            ip_address: User IP address
            user_agent: User agent string
            
        Returns:
            PaymentTransaction instance
        """
        try:
            # Validate amount
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise PaymentServiceError("Invalid amount")
            
            # Create transaction record
            transaction = PaymentTransaction.objects.create(
                user=user,
                provider=PaymentProvider.GOOGLE_PAY,
                amount=amount_decimal,
                currency=currency,
                description=description or f"Google Pay payment of {amount} {currency}",
                status=TransactionStatus.PROCESSING,
                provider_token=token,
                ip_address=ip_address,
                user_agent=user_agent,
                provider_response={
                    'token_received': True,
                    'token_length': len(token),
                    'environment': self.environment,
                    'merchant_id': self.merchant_id
                }
            )
            
            # In a real implementation, you would:
            # 1. Validate the Google Pay token with Google's servers
            # 2. Process the payment with your payment processor
            # 3. Handle the response and update transaction status
            
            # For demo purposes, we'll simulate successful processing
            logger.info(f"Processing Google Pay payment: {transaction.transaction_id}")
            
            # Simulate payment processing
            success = self._simulate_payment_processing(token)
            
            if success:
                transaction.status = TransactionStatus.COMPLETED
                transaction.completed_at = timezone.now()
                transaction.provider_response.update({
                    'processed_at': timezone.now().isoformat(),
                    'simulation_result': 'success',
                    'demo_mode': True
                })
                logger.info(f"Google Pay payment completed: {transaction.transaction_id}")
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.provider_response.update({
                    'processed_at': timezone.now().isoformat(),
                    'simulation_result': 'failed',
                    'demo_mode': True,
                    'error': 'Simulated payment failure'
                })
                logger.warning(f"Google Pay payment failed: {transaction.transaction_id}")
            
            transaction.save()
            return transaction
            
        except Exception as e:
            logger.error(f"Google Pay payment processing error: {str(e)}")
            if 'transaction' in locals():
                transaction.status = TransactionStatus.FAILED
                transaction.provider_response.update({
                    'error': str(e),
                    'demo_mode': True
                })
                transaction.save()
                return transaction
            raise PaymentServiceError(f"Payment processing failed: {str(e)}")
    
    def _simulate_payment_processing(self, token: str) -> bool:
        """
        Simulate payment processing for demo purposes
        In production, this would integrate with actual payment processors
        """
        # Simple simulation: fail if token contains 'fail'
        return 'fail' not in token.lower()
    
    def verify_token(self, token: str) -> Dict:
        """
        Verify Google Pay token (placeholder for actual implementation)
        """
        # In production, you would verify the token with Google's servers
        # and/or your payment processor
        return {
            'valid': True,
            'demo_mode': True,
            'token_info': {
                'length': len(token),
                'environment': self.environment
            }
        }


class PayPalService:
    """Service class for PayPal payment processing"""
    
    def __init__(self):
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.secret_key = getattr(settings, 'PAYPAL_SECRET_KEY', '')
        self.base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')
        self._access_token = None
        self._token_expires_at = None
    
    def _get_basic_auth_header(self) -> str:
        """Generate basic auth header for PayPal API authentication"""
        credentials = f"{self.client_id}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _get_access_token(self) -> str:
        """Get OAuth access token from PayPal"""
        # Check if we have a valid cached token
        if self._access_token and self._token_expires_at:
            if timezone.now() < self._token_expires_at:
                return self._access_token

        # Request new access token
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Authorization": self._get_basic_auth_header(),
        }
        data = "grant_type=client_credentials"

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            
            # Set expiration time (subtract 60 seconds for safety)
            expires_in = token_data.get("expires_in", 32400)  # Default 9 hours
            self._token_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in - 60)
            
            logger.info("Successfully obtained PayPal access token")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise PaymentServiceError(f"Failed to authenticate with PayPal: {e}")
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request to PayPal"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}",
            "PayPal-Request-Id": f"request-{timezone.now().timestamp()}",
        }

        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            else:
                raise PaymentServiceError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    logger.error(f"PayPal API error details: {error_details}")
                except:
                    logger.error(f"PayPal API error response: {e.response.text}")
            raise PaymentServiceError(f"PayPal API request failed: {e}")
    
    def create_order(self, user: User, amount: str, currency: str = "USD", description: str = "", ip_address: str = None, user_agent: str = None) -> Tuple[str, PaymentTransaction]:
        """
        Create a PayPal order
        
        Returns:
            Tuple of (order_id, transaction_instance)
        """
        try:
            # Validate amount
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise PaymentServiceError("Invalid amount")
            
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency,
                            "value": str(amount_decimal)
                        },
                        "description": description or f"Payment of {amount} {currency}"
                    }
                ],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "brand_name": "Technobits Directory",
                            "locale": "en-US",
                            "landing_page": "LOGIN",
                            "user_action": "PAY_NOW"
                        }
                    }
                }
            }

            response = self._make_api_request("POST", "/v2/checkout/orders", order_data)
            order_id = response["id"]
            
            # Create transaction record
            transaction = PaymentTransaction.objects.create(
                user=user,
                provider=PaymentProvider.PAYPAL,
                amount=amount_decimal,
                currency=currency,
                description=description or f"PayPal payment of {amount} {currency}",
                status=TransactionStatus.CREATED,
                provider_order_id=order_id,
                provider_response=response,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"Created PayPal order: {order_id} for transaction: {transaction.transaction_id}")
            return order_id, transaction

        except PaymentServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating PayPal order: {e}")
            raise PaymentServiceError(f"Failed to create order: {e}")
    
    def capture_order(self, order_id: str) -> Tuple[bool, Dict, PaymentTransaction]:
        """
        Capture a PayPal order
        
        Returns:
            Tuple of (success_boolean, response_dict, transaction_instance)
        """
        try:
            # Find the transaction
            transaction = PaymentTransaction.objects.get(
                provider=PaymentProvider.PAYPAL,
                provider_order_id=order_id
            )
            
            # Update status to processing
            transaction.status = TransactionStatus.PROCESSING
            transaction.save()
            
            response = self._make_api_request("POST", f"/v2/checkout/orders/{order_id}/capture")
            
            # Check if capture was successful
            status = response.get("status", "").upper()
            success = status == "COMPLETED"
            
            # Update transaction
            transaction.provider_response = response
            
            if success:
                transaction.status = TransactionStatus.COMPLETED
                transaction.completed_at = timezone.now()
                
                # Extract payment ID from response
                if 'purchase_units' in response:
                    for unit in response['purchase_units']:
                        if 'payments' in unit and 'captures' in unit['payments']:
                            for capture in unit['payments']['captures']:
                                transaction.provider_payment_id = capture.get('id')
                                break
                
                logger.info(f"Successfully captured PayPal order: {order_id}")
            else:
                transaction.status = TransactionStatus.FAILED
                logger.warning(f"PayPal order capture not completed. Status: {status}")
            
            transaction.save()
            return success, response, transaction

        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction not found for PayPal order: {order_id}")
            raise PaymentServiceError("Transaction not found")
        except PaymentServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error capturing PayPal order: {e}")
            raise PaymentServiceError(f"Failed to capture order: {e}")
    
    def get_order_details(self, order_id: str) -> Dict:
        """Get details of a PayPal order"""
        try:
            response = self._make_api_request("GET", f"/v2/checkout/orders/{order_id}")
            logger.info(f"Successfully retrieved order details for: {order_id}")
            return response
        except PaymentServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order details: {e}")
            raise PaymentServiceError(f"Failed to get order details: {e}")


class UnifiedPaymentService:
    """Unified service for all payment providers"""
    
    def __init__(self):
        self.google_pay = GooglePayService()
        self.paypal = PayPalService()
    
    def get_user_transactions(self, user: User, limit: int = 10) -> list:
        """Get user's recent transactions"""
        return PaymentTransaction.objects.filter(user=user).order_by('-created_at')[:limit]
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction by ID"""
        try:
            return PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return None
    
    def get_analytics_data(self, user: User = None) -> Dict:
        """Get payment analytics data"""
        queryset = PaymentTransaction.objects.all()
        if user:
            queryset = queryset.filter(user=user)
        
        total_transactions = queryset.count()
        completed_transactions = queryset.filter(status=TransactionStatus.COMPLETED).count()
        
        # Provider breakdown
        google_pay_count = queryset.filter(provider=PaymentProvider.GOOGLE_PAY).count()
        paypal_count = queryset.filter(provider=PaymentProvider.PAYPAL).count()
        
        # Amount calculations
        completed_queryset = queryset.filter(status=TransactionStatus.COMPLETED)
        total_amount = sum(t.amount for t in completed_queryset) if completed_queryset.exists() else 0
        
        return {
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'success_rate': (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            'total_amount': float(total_amount),
            'provider_breakdown': {
                'google_pay': google_pay_count,
                'paypal': paypal_count
            },
            'recent_transactions': [
                {
                    'id': t.transaction_id,
                    'provider': t.provider,
                    'amount': float(t.amount),
                    'currency': t.currency,
                    'status': t.status,
                    'created_at': t.created_at.isoformat()
                }
                for t in queryset.order_by('-created_at')[:10]
            ]
        }
