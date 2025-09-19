'use client'

import { useState, useCallback, useEffect } from 'react'
import PayPalButton from '@/components/PayPalButton'
import { useNotification } from '../contexts/NotificationContext'

export default function Home() {
  const { showNotification } = useNotification()
  const [amount, setAmount] = useState<string>('10.00')
  const [description, setDescription] = useState<string>('Sample Product Purchase')
  const [debouncedAmount, setDebouncedAmount] = useState<string>('10.00')
  const [debouncedDescription, setDebouncedDescription] = useState<string>('Sample Product Purchase')

  // Reset form to initial state (simple version)
  const resetForm = useCallback(() => {
    setAmount('10.00')
    setDescription('Sample Product Purchase')
    setDebouncedAmount('10.00')
    setDebouncedDescription('Sample Product Purchase')
  }, [])

  // Debounced update using useEffect with longer delay for better UX
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedAmount(amount)
    }, 800) // Longer delay to prevent button flickering
    
    return () => clearTimeout(timer)
  }, [amount])

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedDescription(description)
    }, 800) // Longer delay to prevent button flickering
    
    return () => clearTimeout(timer)
  }, [description])

  // Input handlers for smooth typing
  const handleAmountChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Allow empty value or valid decimal numbers
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmount(value)
    }
  }, [])

  const handleDescriptionChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setDescription(e.target.value)
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          PayPal Checkout Demo
        </h2>
        <p className="text-xl text-gray-600">
          Test the complete PayPal integration flow
        </p>
      </div>

      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="mb-6">
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
            Amount (USD)
          </label>
          <input
            type="text"
            id="amount"
            value={amount}
            onChange={handleAmountChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-paypal-blue focus:border-paypal-blue transition-all duration-200"
            placeholder="Enter amount (e.g., 10.00)"
          />
        </div>

        <div className="mb-6">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <input
            type="text"
            id="description"
            value={description}
            onChange={handleDescriptionChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-paypal-blue focus:border-paypal-blue transition-all duration-200"
            placeholder="Enter description"
          />
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Payment Options
          </h3>
          
          {/* Show current values to user with typing indicator */}
          <div className="mb-4 p-3 bg-blue-50 rounded-md transition-all duration-200">
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
                  (will update...)
                </span>
              )}
            </p>
            {(amount !== debouncedAmount || description !== debouncedDescription) && (
              <p className="text-xs text-blue-600 mt-1 italic">
                💡 PayPal buttons will update automatically when you stop typing
              </p>
            )}
          </div>
          
          <PayPalButton
            amount={debouncedAmount}
            currency="USD"
            description={debouncedDescription}
            onSuccess={(details) => {
              console.log('Payment successful:', details)
              showNotification({
                type: 'success',
                title: '🎉 Payment Successful!',
                message: `Your payment has been completed successfully. Transaction ID: ${details.transaction_id}`,
                duration: 6000
              })
              
              // Reset form to initial state after successful payment
              setTimeout(() => {
                resetForm()
              }, 2000) // Wait 2 seconds before resetting to let user see the success message
            }}
            onError={(error) => {
              console.error('Payment error:', error)
              // Only show notification for actual payment errors, not initialization/zoid errors
              if (error.message && 
                  !error.message.includes('load') && 
                  !error.message.includes('SDK') && 
                  !error.message.includes('container element removed') &&
                  !error.message.includes('zoid destroyed') &&
                  !error.message.includes('destroyed all components')) {
                showNotification({
                  type: 'error',
                  title: '❌ Payment Failed',
                  message: `We couldn't process your payment: ${error.message || 'Unknown error'}. Please try again.`,
                  duration: 8000
                })
              }
            }}
          />
        </div>
      </div>

    </div>
  )
}
