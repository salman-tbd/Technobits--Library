"use client";

import { useAuth } from "../../../contexts/AuthContext";
import { useNotification } from "../../../contexts/NotificationContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeftIcon, GlobeAltIcon } from "@heroicons/react/24/outline";
import PayPalButton from "../../../components/payments/PayPalButton";
import PaymentSuccessModal from "../../../components/payments/PaymentSuccessModal";

export default function PayPalCheckout() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const { showNotification } = useNotification();
  const router = useRouter();
  const [amount, setAmount] = useState('10.00');
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [paymentResult, setPaymentResult] = useState<any>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login?redirect=/checkout/paypal');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading PayPal checkout...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
              </Link>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <GlobeAltIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">PayPal Demo</h1>
                  <p className="text-sm text-gray-500">Global Payment Integration</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {user?.name || user?.email?.split('@')[0]}
              </p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div 
          className="space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Info Section */}
          <div className="text-center mb-12">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-white text-3xl">🅿️</span>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">PayPal Integration Demo</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience global payment processing with PayPal Orders API v2. 
              Complete with webhooks, transaction management, and international support.
            </p>
          </div>

          {/* Payment Form */}
          <div className="max-w-md mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Payment Details</h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount (USD)
                  </label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    placeholder="Enter amount"
                    min="1"
                    step="0.01"
                  />
                </div>

                {/* Real PayPal Button */}
                <div className="space-y-4">
                  <PayPalButton
                    amount={amount}
                    currency="USD"
                    description={`Payment for $${amount} USD`}
                    onSuccess={(result) => {
                      console.log('PayPal payment successful:', result);
                      // Store payment result and show modal
                      setPaymentResult({
                        amount,
                        currency: 'USD',
                        provider: 'paypal',
                        transactionId: result.orderID || result.id || 'PP-' + Date.now()
                      });
                      setShowSuccessModal(true);
                      // Reset amount after successful payment
                      setTimeout(() => {
                        setAmount('10.00');
                      }, 2000);
                    }}
                    onError={(error) => {
                      console.error('PayPal payment error:', error);
                      showNotification({
                        type: 'error',
                        title: '❌ Payment Failed',
                        message: `PayPal payment failed: ${error.message || 'Unknown error'}. Please try again.`,
                        duration: 8000
                      });
                    }}
                    onCancel={() => {
                      console.log('PayPal payment cancelled');
                      showNotification({
                        type: 'warning',
                        title: '⚠️ Payment Cancelled',
                        message: 'PayPal payment was cancelled by user.',
                        duration: 4000
                      });
                    }}
                    disabled={!amount || parseFloat(amount) <= 0}
                  />
                </div>

                {/* Payment Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-800 mb-2">Payment Summary</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-blue-700">Amount:</span>
                      <span className="font-medium text-blue-900">${amount} USD</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Currency:</span>
                      <span className="font-medium text-blue-900">USD</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Environment:</span>
                      <span className="font-medium text-blue-900">Sandbox</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="mt-8 space-y-4">
              <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
                <h4 className="font-semibold text-gray-900 mb-3">PayPal Features</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-600 text-sm">🌍</span>
                    <span className="text-sm text-gray-600">Global Payments</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-600 text-sm">🔗</span>
                    <span className="text-sm text-gray-600">Webhook Support</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-600 text-sm">📊</span>
                    <span className="text-sm text-gray-600">Transaction Logs</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-600 text-sm">⚡</span>
                    <span className="text-sm text-gray-600">Real-time Processing</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Link 
                href="/checkout/google-pay"
                className="flex-1 inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all"
              >
                ← Try Google Pay
              </Link>
              <Link 
                href="/analytics"
                className="flex-1 inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all"
              >
                View Analytics →
              </Link>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Payment Success Modal */}
      {paymentResult && (
        <PaymentSuccessModal
          isOpen={showSuccessModal}
          onClose={() => setShowSuccessModal(false)}
          paymentDetails={paymentResult}
          autoRedirect={true}
          redirectPath="/analytics"
        />
      )}
    </div>
  );
}
