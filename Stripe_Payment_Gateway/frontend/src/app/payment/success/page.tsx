'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircle, CreditCard, Download, ArrowLeft, Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { paymentsApi } from '@/lib/api/payments';

export default function PaymentSuccess() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [paymentDetails, setPaymentDetails] = useState<any>(null);

  useEffect(() => {
    const fetchSessionStatus = async () => {
      if (sessionId) {
        try {
          const response = await paymentsApi.getSessionStatus(sessionId);
          if (response.success && response.data) {
            setPaymentDetails({
              id: sessionId,
              amount: 2999, // Default amount, could be passed via URL params
              currency: 'USD',
              description: 'Premium Service Demo',
              status: response.data.payment_status,
              customer_email: response.data.customer_email,
              created: Date.now(),
            });
          } else {
            // Fallback to default data if API fails
            setPaymentDetails({
              id: sessionId,
              amount: 2999,
              currency: 'USD', 
              description: 'Premium Service Demo',
              status: 'succeeded',
              created: Date.now(),
            });
          }
        } catch (error) {
          console.error('Failed to fetch session status:', error);
          // Fallback to default data
          setPaymentDetails({
            id: sessionId,
            amount: 2999,
            currency: 'USD',
            description: 'Premium Service Demo', 
            status: 'succeeded',
            created: Date.now(),
          });
        }
      }
    };

    fetchSessionStatus();
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-200 overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-8 py-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4">
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Payment Successful!</h1>
            <p className="text-green-100">Your transaction has been completed</p>
          </div>

          {/* Payment Details */}
          <div className="p-8 space-y-6">
            {paymentDetails && (
              <>
                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <h2 className="font-semibold text-gray-900 flex items-center">
                    <CreditCard className="h-5 w-5 mr-2 text-blue-600" />
                    Payment Details
                  </h2>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Amount</span>
                      <span className="font-semibold text-gray-900">
                        ${(paymentDetails.amount / 100).toFixed(2)} {paymentDetails.currency}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Description</span>
                      <span className="font-medium text-gray-900">{paymentDetails.description}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Transaction ID</span>
                      <span className="font-mono text-sm text-gray-700">
                        {paymentDetails.id.slice(0, 20)}...
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status</span>
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        {paymentDetails.status}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Date</span>
                      <span className="text-gray-900">
                        {new Date(paymentDetails.created).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* What's Next */}
                <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200">
                  <h3 className="font-semibold text-blue-900 mb-3">What's Next?</h3>
                  <ul className="space-y-2 text-sm text-blue-800">
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                      You'll receive a confirmation email shortly
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                      Your service will be activated within 24 hours
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                      Check your account dashboard for updates
                    </li>
                  </ul>
                </div>
              </>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button 
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-semibold"
                onClick={() => window.location.href = '/'}
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to Home
              </Button>
            </div>
            {/* Security Note */}
            <div className="text-center pt-4">
              <p className="text-xs text-gray-500">
                This transaction was processed securely by Stripe
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

