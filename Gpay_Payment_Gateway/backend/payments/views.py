import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import PaymentTransaction

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def process_payment(request):
    try:
        data = json.loads(request.body)
        token = data.get('token')
        amount = data.get('amount')
        
        if not token or not amount:
            return JsonResponse({
                'status': 'error',
                'message': 'Token and amount are required'
            }, status=400)
        
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid amount'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid amount format'
            }, status=400)
        
        # Create transaction ID
        transaction_id = f'gpay_{amount}_{token[:10]}'
        
        # Log the payment data for testing
        logger.info(f"Received Google Pay payment - Amount: {amount} INR, Token: {token[:50]}...")
        
        # Save transaction to database
        try:
            transaction = PaymentTransaction.objects.create(
                transaction_id=transaction_id,
                amount=amount_float,
                currency='INR',
                google_pay_token=token,
                status='success'
            )
            logger.info(f"Transaction saved to database: {transaction_id}")
        except Exception as e:
            logger.error(f"Failed to save transaction: {str(e)}")
        
        # Process Google Pay payment (here you would validate the token and process payment)
        # For now, just return success response for testing
        
        return JsonResponse({
            'status': 'success',
            'message': 'Google Pay payment received successfully',
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': 'INR'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


