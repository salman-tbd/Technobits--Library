"""
Simple views for Stripe Payment Gateway.
"""

import json
import stripe
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StripeTransaction


# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')


@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    """
    Create a simple Stripe Payment Intent.
    """
    try:
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', 'USD').lower()
        description = data.get('description', '')
        
        # Create Payment Intent in Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            description=description,
            automatic_payment_methods={'enabled': True},
        )
        
        # Create local transaction record
        transaction = StripeTransaction.objects.create(
            transaction_id=f"pi_{intent.id}",
            stripe_payment_intent_id=intent.id,
            amount=amount,
            currency=currency.upper(),
            description=description,
            status='pending',
            stripe_response=dict(intent)
        )
        
        return JsonResponse({
            'success': True,
            'client_secret': intent.client_secret,
            'transaction_id': transaction.transaction_id,
            'message': 'Payment Intent created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to create Payment Intent'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def create_checkout_session(request):
    """
    Create a simple Stripe Checkout Session.
    """
    try:
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', 'USD').lower()
        description = data.get('description', 'Payment')
        success_url = data.get('success_url', f"{request.build_absolute_uri('/')[:-1]}/payment/success/")
        cancel_url = data.get('cancel_url', f"{request.build_absolute_uri('/')[:-1]}/payment/cancel/")
        
        # Create Checkout Session in Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': description,
                    },
                    'unit_amount': int(amount * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
        )
        
        # Create local transaction record
        transaction = StripeTransaction.objects.create(
            transaction_id=f"cs_{session.id}",
            stripe_session_id=session.id,
            amount=amount,
            currency=currency.upper(),
            description=description,
            status='pending',
            stripe_response=dict(session)
        )
        
        return JsonResponse({
            'success': True,
            'checkout_url': session.url,
            'session_id': session.id,
            'transaction_id': transaction.transaction_id,
            'message': 'Checkout Session created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to create Checkout Session'
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def session_status(request):
    """
    Get session status from Stripe.
    """
    try:
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id parameter is required',
                'message': 'Missing session_id'
            }, status=400)
        
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Update local transaction if exists
        try:
            transaction = StripeTransaction.objects.get(stripe_session_id=session_id)
            transaction.status = session.payment_status
            transaction.stripe_payment_intent_id = session.payment_intent
            transaction.stripe_response = dict(session)
            transaction.save()
        except StripeTransaction.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'data': {
                'session_id': session.id,
                'payment_status': session.payment_status,
                'customer_email': session.customer_details.email if session.customer_details else None,
            },
            'message': 'Session status retrieved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve session status'
        }, status=400)


class PaymentListView(APIView):
    """
    Simple API view to list transactions.
    """
    
    def get(self, request):
        """Get list of transactions."""
        transactions = StripeTransaction.objects.all()[:20]  # Limit to 20 recent transactions
        
        data = []
        for transaction in transactions:
            data.append({
                'id': transaction.id,
                'transaction_id': transaction.transaction_id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'data': data,
            'count': len(data),
            'message': 'Transactions retrieved successfully'
        })


class PaymentDetailView(APIView):
    """
    Simple API view to get transaction details.
    """
    
    def get(self, request, pk):
        """Get transaction details."""
        try:
            transaction = StripeTransaction.objects.get(pk=pk)
            
            data = {
                'id': transaction.id,
                'transaction_id': transaction.transaction_id,
                'stripe_session_id': transaction.stripe_session_id,
                'stripe_payment_intent_id': transaction.stripe_payment_intent_id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat(),
                'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
                'stripe_response': transaction.stripe_response,
            }
            
            return Response({
                'success': True,
                'data': data,
                'message': 'Transaction details retrieved successfully'
            })
            
        except StripeTransaction.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Transaction not found',
                'message': 'Transaction not found'
            }, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def payment_stats(request):
    """
    Get basic payment statistics.
    """
    try:
        total_transactions = StripeTransaction.objects.count()
        successful_transactions = StripeTransaction.objects.filter(status='succeeded').count()
        pending_transactions = StripeTransaction.objects.filter(status='pending').count()
        failed_transactions = StripeTransaction.objects.filter(status='failed').count()
        
        # Calculate total amounts
        successful_amount = sum(
            t.amount for t in StripeTransaction.objects.filter(status='succeeded')
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_transactions': total_transactions,
                'successful_transactions': successful_transactions,
                'pending_transactions': pending_transactions,
                'failed_transactions': failed_transactions,
                'successful_amount': str(successful_amount),
                'success_rate': round((successful_transactions / total_transactions * 100), 2) if total_transactions > 0 else 0,
            },
            'message': 'Payment statistics retrieved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve payment statistics'
        }, status=400)


# Placeholder views for URL compatibility
def create_refund(request, payment_id):
    """Placeholder for refund creation."""
    return JsonResponse({
        'success': False,
        'message': 'Refund functionality not implemented in this simple version'
    }, status=501)


class RefundListView(APIView):
    """Placeholder for refund list."""
    def get(self, request):
        return Response({
            'success': False,
            'message': 'Refund functionality not implemented in this simple version'
        }, status=501)


class PaymentMethodListView(APIView):
    """Placeholder for payment method list."""
    def get(self, request):
        return Response({
            'success': False,
            'message': 'Payment method management not implemented in this simple version'
        }, status=501)


def delete_payment_method(request, payment_method_id):
    """Placeholder for payment method deletion."""
    return JsonResponse({
        'success': False,
        'message': 'Payment method management not implemented in this simple version'
    }, status=501)


class PaymentEventListView(APIView):
    """Placeholder for payment event list."""
    def get(self, request):
        return Response({
            'success': False,
            'message': 'Payment event tracking not implemented in this simple version'
        }, status=501)
