'use client';

import { XCircle, ArrowLeft, RefreshCw, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PaymentCancel() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-200 overflow-hidden">
          {/* Cancel Header */}
          <div className="bg-gradient-to-r from-red-500 to-pink-600 px-8 py-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4">
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Payment Cancelled</h1>
            <p className="text-red-100">Your transaction was not completed</p>
          </div>

          {/* Content */}
          <div className="p-8 space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Don't worry, no charges were made
              </h2>
              <p className="text-gray-600">
                You can try again anytime. If you encountered any issues, 
                our support team is here to help.
              </p>
            </div>

            {/* Common Reasons */}
            <div className="bg-gray-50 rounded-2xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Common reasons for cancellation:</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Changed your mind about the purchase
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Wanted to review the details again
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Technical issue with the payment form
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Need to use a different payment method
                </li>
              </ul>
            </div>

            {/* Help Section */}
            <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <HelpCircle className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">Need Help?</h3>
                  <p className="text-sm text-blue-800 mb-3">
                    If you're experiencing technical issues or have questions about our services, 
                    we're here to assist you.
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="border-blue-300 text-blue-700 hover:bg-blue-100"
                  >
                    Contact Support
                  </Button>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button 
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-semibold"
                onClick={() => window.location.href = '/'}
              >
                <RefreshCw className="h-5 w-5 mr-2" />
                Try Again
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full h-10 rounded-xl border-2"
                onClick={() => window.location.href = '/'}
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to Home
              </Button>
            </div>

            {/* Security Note */}
            <div className="text-center pt-4">
              <p className="text-xs text-gray-500">
                Your payment information was handled securely and has been discarded
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


