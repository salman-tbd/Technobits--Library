"""
PayPal API Service Classes
"""
import requests
import base64
import json
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class PayPalAPIError(Exception):
    """Custom exception for PayPal API errors"""
    pass


class PayPalService:
    """
    Service class to handle PayPal API interactions
    """
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret_key = settings.PAYPAL_SECRET_KEY
        self.base_url = settings.PAYPAL_BASE_URL
        self._access_token = None
        self._token_expires_at = None

    def _get_basic_auth_header(self) -> str:
        """Generate basic auth header for PayPal API authentication"""
        credentials = f"{self.client_id}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    def _get_access_token(self) -> str:
        """
        Get OAuth access token from PayPal
        Caches token until it expires
        """
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
            raise PayPalAPIError(f"Failed to authenticate with PayPal: {e}")

    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make authenticated API request to PayPal
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}",
            "PayPal-Request-Id": f"request-{timezone.now().timestamp()}",  # Idempotency
        }

        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            else:
                raise PayPalAPIError(f"Unsupported HTTP method: {method}")

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
            raise PayPalAPIError(f"PayPal API request failed: {e}")

    def create_order(self, amount: str, currency: str = "USD", description: str = "") -> Tuple[str, Dict]:
        """
        Create a PayPal order
        
        Args:
            amount: Order amount as string (e.g., "10.00")
            currency: Currency code (default: "USD")
            description: Order description
            
        Returns:
            Tuple of (order_id, full_response)
        """
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": amount
                    },
                    "description": description or f"Payment of {amount} {currency}"
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "Your Store Name",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        "user_action": "PAY_NOW"
                    }
                }
            }
        }

        try:
            response = self._make_api_request("POST", "/v2/checkout/orders", order_data)
            order_id = response["id"]
            logger.info(f"Successfully created PayPal order: {order_id}")
            return order_id, response

        except PayPalAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating PayPal order: {e}")
            raise PayPalAPIError(f"Failed to create order: {e}")

    def capture_order(self, order_id: str) -> Tuple[bool, Dict]:
        """
        Capture a PayPal order
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Tuple of (success_boolean, full_response)
        """
        try:
            response = self._make_api_request("POST", f"/v2/checkout/orders/{order_id}/capture")
            
            # Check if capture was successful
            status = response.get("status", "").upper()
            success = status == "COMPLETED"
            
            if success:
                logger.info(f"Successfully captured PayPal order: {order_id}")
            else:
                logger.warning(f"PayPal order capture not completed. Status: {status}")
            
            return success, response

        except PayPalAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error capturing PayPal order: {e}")
            raise PayPalAPIError(f"Failed to capture order: {e}")

    def get_order_details(self, order_id: str) -> Dict:
        """
        Get details of a PayPal order
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Order details dictionary
        """
        try:
            response = self._make_api_request("GET", f"/v2/checkout/orders/{order_id}")
            logger.info(f"Successfully retrieved order details for: {order_id}")
            return response

        except PayPalAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order details: {e}")
            raise PayPalAPIError(f"Failed to get order details: {e}")

    def verify_webhook_signature(self, headers: Dict, body: str, webhook_id: str) -> bool:
        """
        Verify PayPal webhook signature (optional but recommended)
        
        Args:
            headers: Request headers
            body: Raw request body
            webhook_id: PayPal webhook ID
            
        Returns:
            True if signature is valid, False otherwise
        """
        # This is a simplified implementation
        # In production, implement proper webhook signature verification
        # See: https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature
        
        try:
            # PayPal webhook verification would go here
            # For now, we'll do basic validation
            required_headers = ['paypal-transmission-id', 'paypal-cert-id', 'paypal-transmission-sig']
            return all(header in headers for header in required_headers)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
