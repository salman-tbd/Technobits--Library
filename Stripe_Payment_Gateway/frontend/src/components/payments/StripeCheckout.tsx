/**
 * Stripe Checkout Component
 * Simplified Stripe integration for the reference project
 */

'use client';

import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { 
  CreditCard, 
  Shield, 
  Lock, 
  CheckCircle, 
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';

import { Button } from '@/components/ui/button';
import { paymentsApi } from '@/lib/api/payments';
import type { CreateCheckoutSessionRequest } from '@/types/payment';

// Initialize Stripe
const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''
);

interface StripeCheckoutProps {
  amount?: number;
  currency?: string;
  description?: string;
  onSuccess?: (sessionId: string) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
  className?: string;
}

export const StripeCheckout: React.FC<StripeCheckoutProps> = ({
  amount = 29.99,
  currency = 'USD',
  description = 'Payment',
  onSuccess,
  onError,
  onCancel,
  className = ''
}) => {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    if (!amount || amount <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    setLoading(true);

    try {
      const checkoutData: CreateCheckoutSessionRequest = {
        amount: amount,
        currency,
        description: description,
        success_url: `${window.location.origin}/payment/success`,
        cancel_url: `${window.location.origin}/payment/cancel`,
      };

      const response = await paymentsApi.createCheckoutSession(checkoutData);

      if (response.success && response.data?.checkout_url) {
        // Redirect to Stripe Checkout
        window.location.href = response.data.checkout_url;
        
        if (onSuccess) {
          onSuccess(response.data.session_id);
        }
      } else {
        const errorMessage = response.message || 'Failed to create checkout session';
        toast.error(errorMessage);
        if (onError) {
          onError(errorMessage);
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Payment failed';
      toast.error(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount);
  };


  return (
    <div className={className}>
      {/* Payment Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200 mb-6">
        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
          <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
          Payment Summary
        </h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Amount:</span>
            <span className="font-bold text-lg text-gray-900">
              {formatCurrency(amount || 0, currency)}
            </span>
          </div>
          <div className="flex justify-between items-start">
            <span className="text-sm text-gray-600">Description:</span>
            <span className="text-sm text-gray-900 text-right max-w-xs">
              {description || 'No description provided'}
            </span>
          </div>
        </div>
      </div>

      {/* Security Badge */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-4 border border-green-200 mb-6">
        <div className="flex items-start space-x-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <Lock className="h-5 w-5 text-green-600" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 mb-1">Bank-Level Security</h4>
            <p className="text-sm text-gray-600 mb-2">
              Your payment information is encrypted and processed securely by Stripe. 
              We never store your card details.
            </p>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span className="flex items-center">
                <CheckCircle className="h-3 w-3 mr-1 text-green-500" />
                SSL Encrypted
              </span>
              <span className="flex items-center">
                <CheckCircle className="h-3 w-3 mr-1 text-green-500" />
                PCI Compliant
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <Button
        onClick={handleCheckout}
        disabled={loading || !amount || amount <= 0}
        className="w-full h-12 text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02]"
      >
        {loading ? (
          <div className="flex items-center space-x-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Processing...</span>
          </div>
        ) : (
          <div className="flex items-center justify-center space-x-2">
            <Lock className="h-5 w-5" />
            <span>Pay {formatCurrency(amount || 0, currency)}</span>
          </div>
        )}
      </Button>

      {/* Test Card Info */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mt-6">
        <div className="flex items-start space-x-3">
          <div className="p-1 bg-yellow-100 rounded">
            <CreditCard className="h-4 w-4 text-yellow-600" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-yellow-800 text-sm mb-1">Test Mode</h4>
            <p className="text-xs text-yellow-700 mb-2">
              Use these test card numbers for demo:
            </p>
            <div className="grid grid-cols-1 gap-1 text-xs text-yellow-700">
              <div className="flex justify-between">
                <span className="font-mono">4242 4242 4242 4242</span>
                <span className="text-green-600 font-medium">✓ Success</span>
              </div>
              <div className="flex justify-between">
                <span className="font-mono">4000 0000 0000 0002</span>
                <span className="text-red-600 font-medium">✗ Decline</span>
              </div>
            </div>
            <p className="text-xs text-yellow-600 mt-1">
              Any future date, any CVC, any ZIP code
            </p>
          </div>
        </div>
      </div>

      {/* Powered by Stripe */}
      <div className="text-center pt-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-gray-100 rounded-full">
          <span className="text-xs text-gray-500">Secured by</span>
          <div className="flex items-center space-x-1">
            <Shield className="h-3 w-3 text-blue-600" />
            <span className="text-xs font-semibold text-gray-700">Stripe</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StripeCheckout;