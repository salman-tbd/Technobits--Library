'use client';

import { useState, useCallback, useEffect } from 'react';
import { StripeCheckout } from '@/components/payments/StripeCheckout'
import { Shield, CreditCard } from 'lucide-react'

export default function Home() {
  const [amount, setAmount] = useState<string>('29.99');
  const [description, setDescription] = useState<string>('Premium Service Demo');
  const [debouncedAmount, setDebouncedAmount] = useState<string>('29.99');
  const [debouncedDescription, setDebouncedDescription] = useState<string>('Premium Service Demo');

  // Reset form to initial state
  const resetForm = useCallback(() => {
    setAmount('29.99');
    setDescription('Premium Service Demo');
    setDebouncedAmount('29.99');
    setDebouncedDescription('Premium Service Demo');
  }, []);

  // Debounced update using useEffect
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedAmount(amount);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [amount]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedDescription(description);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [description]);

  // Input handlers
  const handleAmountChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow empty value or valid decimal numbers
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmount(value);
    }
  }, []);

  const handleDescriptionChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setDescription(e.target.value);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                <CreditCard className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Stripe Payment Gateway
                </h1>
                <p className="text-sm text-gray-500">Secure payment processing</p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Badge */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-t border-green-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
            <div className="flex items-center justify-center space-x-2 text-xs text-green-700">
              <Shield className="h-3 w-3" />
              <span>Bank-level security • PCI DSS compliant • SSL encrypted</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          {/* Form Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
            <h3 className="text-xl font-bold text-white text-center">Payment Details</h3>
          </div>

          <div className="p-6">
            {/* Amount Input */}
            <div className="mb-6">
              <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                Amount (USD)
              </label>
              <input
                type="text"
                id="amount"
                value={amount}
                onChange={handleAmountChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 text-gray-900 placeholder-gray-500"
                placeholder="Enter amount (e.g., 29.99)"
              />
            </div>

            {/* Description Input */}
            <div className="mb-6">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <input
                type="text"
                id="description"
                value={description}
                onChange={handleDescriptionChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 text-gray-900 placeholder-gray-500"
                placeholder="Enter description"
              />
            </div>

            {/* Current Values Display */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>Payment Amount:</strong> ${debouncedAmount || '0.00'} USD
                {amount !== debouncedAmount && (
                  <span className="ml-2 text-xs text-blue-600 italic animate-pulse">
                    (will update to ${amount}...)
                  </span>
                )}
              </p>
              <p className="text-sm text-blue-800">
                <strong>Description:</strong> {debouncedDescription || 'No description'}
                {description !== debouncedDescription && (
                  <span className="ml-2 text-xs text-blue-600 italic animate-pulse">
                    (updating...)
                  </span>
                )}
              </p>
              {(amount !== debouncedAmount || description !== debouncedDescription) && (
                <p className="text-xs text-blue-600 mt-1 italic">
                  💡 Payment form will update when you stop typing
                </p>
              )}
            </div>

            {/* Stripe Checkout Component */}
            <StripeCheckout
              amount={parseFloat(debouncedAmount) || 0}
              currency="USD"
              description={debouncedDescription}
              onSuccess={(sessionId) => {
                console.log('Payment successful:', sessionId);
                // Reset form after successful payment
                setTimeout(() => {
                  resetForm();
                }, 2000);
              }}
              onError={(error) => {
                console.error('Payment error:', error);
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
