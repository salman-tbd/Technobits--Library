"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/solid';
import { useRouter } from 'next/navigation';

interface PaymentSuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  paymentDetails: {
    amount: string;
    currency: string;
    provider: 'google_pay' | 'paypal';
    transactionId?: string;
  };
  autoRedirect?: boolean;
  redirectPath?: string;
}

const PaymentSuccessModal: React.FC<PaymentSuccessModalProps> = ({
  isOpen,
  onClose,
  paymentDetails,
  autoRedirect = true,
  redirectPath = '/analytics'
}) => {
  const router = useRouter();

  const providerNames = {
    google_pay: 'Google Pay',
    paypal: 'PayPal'
  };

  const currencySymbols = {
    USD: '$',
    INR: '₹',
    EUR: '€',
    GBP: '£'
  };

  const handleRedirectToAnalytics = () => {
    onClose();
    router.push(redirectPath);
  };

  // Auto-close after 5 seconds if no user interaction
  useEffect(() => {
    if (isOpen && autoRedirect) {
      const timer = setTimeout(() => {
        handleRedirectToAnalytics();
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [isOpen, autoRedirect]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.7, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.7, y: 20 }}
              transition={{ type: "spring", duration: 0.3 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-auto overflow-hidden"
              style={{
                position: 'relative',
                zIndex: 99999
              }}
            >
              
              {/* Header with success animation */}
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-8 text-center relative">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                  className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4"
                >
                  <CheckCircleIcon className="w-10 h-10 text-green-500" />
                </motion.div>
                
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-2xl font-bold text-white mb-2"
                >
                  Payment Successful!
                </motion.h2>
                
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-green-100"
                >
                  Your payment has been processed successfully
                </motion.p>

                {/* Close button */}
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 text-white hover:text-green-200 transition-colors"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              {/* Payment Details */}
              <div className="px-6 py-6">
                <div className="space-y-4">
                  {/* Amount */}
                  <div className="flex justify-between items-center py-3 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">Amount Paid</span>
                    <span className="text-2xl font-bold text-gray-900">
                      {currencySymbols[paymentDetails.currency as keyof typeof currencySymbols] || paymentDetails.currency + ' '}
                      {paymentDetails.amount}
                    </span>
                  </div>


                  {/* Transaction ID */}
                  {paymentDetails.transactionId && (
                    <div className="py-3">
                      <span className="text-gray-600 font-medium block mb-1">Transaction ID</span>
                      <span className="text-sm text-gray-500 font-mono bg-gray-50 px-3 py-2 rounded-lg break-all">
                        {paymentDetails.transactionId}
                      </span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="mt-8 space-y-3">
                  <motion.div
                    id="success-modal-analytics-btn"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleRedirectToAnalytics}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl cursor-pointer flex items-center justify-center"
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleRedirectToAnalytics();
                      }
                    }}
                  >
                    <span className="flex items-center justify-center">
                      📊 View Analytics
                    </span>
                  </motion.div>
                  
                  <motion.div
                    id="success-modal-continue-btn"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={onClose}
                    className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-all duration-200 cursor-pointer flex items-center justify-center"
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onClose();
                      }
                    }}
                  >
                    <span className="flex items-center justify-center">
                      🛍️ Continue Shopping
                    </span>
                  </motion.div>
                </div>

                {/* Auto-redirect notice */}
                {autoRedirect && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="text-center text-xs text-gray-500 mt-4"
                  >
                    You'll be redirected to analytics in 5 seconds
                  </motion.p>
                )}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default PaymentSuccessModal;
