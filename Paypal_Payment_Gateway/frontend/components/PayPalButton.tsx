'use client'

/**
 * PayPal Button Component
 * 
 * This component handles the complete PayPal checkout flow:
 * 1. Loads PayPal SDK dynamically
 * 2. Creates order via Django backend
 * 3. Handles PayPal approval flow
 * 4. Captures payment via Django backend
 */
import React, { useEffect, useRef, useState, useMemo } from 'react'
import { usePayPalSDK } from '@/hooks/usePayPalSDK'
import { PayPalAPI } from '@/lib/api'
import { PayPalButtonProps, PayPalOrderData } from '@/types/paypal'

const PayPalButton: React.FC<PayPalButtonProps> = ({
  amount,
  currency = 'USD',
  description = '',
  onSuccess,
  onError,
  onCancel,
  disabled = false,
}) => {
  const paypalRef = useRef<HTMLDivElement>(null)
  const buttonsInstanceRef = useRef<any>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [buttonRendered, setButtonRendered] = useState(false)
  const [componentKey, setComponentKey] = useState(0)
  const [isMounted, setIsMounted] = useState(false)

  // Get PayPal Client ID from environment with fallback for development
  const clientId = process.env.PAYPAL_CLIENT_ID || process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID || 'demo-client-id-not-configured'

  // Load PayPal SDK
  const { isLoaded, isLoading, error: sdkError } = usePayPalSDK({ 
    clientId, 
    currency 
  })

  // Validate props
  const isValidAmount = amount && parseFloat(amount) > 0
  const hasClientId = !!clientId && !clientId.includes('demo-client-id-not-configured')

  // Handle initial loading without showing errors immediately
  const showInitialErrors = isLoaded || (!isLoading && sdkError)

  // Stable values to prevent unnecessary re-renders
  const stableProps = useMemo(() => ({
    amount,
    currency,
    description
  }), [amount, currency, description])

  // Cleanup function
  const cleanupPayPalButtons = () => {
    if (buttonsInstanceRef.current) {
      try {
        buttonsInstanceRef.current.close()
      } catch (error: any) {
        // Ignore cleanup errors silently
        console.debug('PayPal cleanup error (expected):', error?.message)
      }
      buttonsInstanceRef.current = null
    }
    if (paypalRef.current) {
      try {
        paypalRef.current.innerHTML = ''
      } catch (error: any) {
        // Ignore DOM cleanup errors
        console.debug('DOM cleanup error (expected):', error?.message)
      }
    }
    setButtonRendered(false)
  }

  // Track last rendered values to prevent unnecessary re-renders
  const lastRenderedValues = useRef({ amount: '', description: '' })
  
  // Only trigger re-render when values actually stabilize (not while typing)
  useEffect(() => {
    // Only re-render if values have actually changed and are different from last render
    if (stableProps.amount !== lastRenderedValues.current.amount || 
        stableProps.description !== lastRenderedValues.current.description) {
      
      // Update tracking
      lastRenderedValues.current = {
        amount: stableProps.amount,
        description: stableProps.description
      }
      
      setComponentKey(prev => prev + 1)
      cleanupPayPalButtons()
    }
  }, [stableProps.amount, stableProps.description])

  // Prevent initial rendering if component just mounted - add delay for Edge compatibility
  useEffect(() => {
    // Add small delay to ensure DOM is ready in Microsoft Edge
    const timer = setTimeout(() => {
      setIsMounted(true)
      console.log('PayPal component mounted and ready');
    }, 150); // Slightly longer delay for Edge compatibility
    
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // Only render after component is mounted and SDK is ready
    if (!isMounted || !isLoaded || !window.paypal || !isValidAmount || !hasClientId) {
      console.log('PayPal button not ready:', { isMounted, isLoaded, hasPayPal: !!window.paypal, isValidAmount, hasClientId });
      return
    }

    if (!paypalRef.current) {
      console.log('PayPal container ref not available');
      return
    }

    // Only render if we have valid values (prevents rendering during typing)
    if (!amount || parseFloat(amount) <= 0) {
      console.log('Invalid amount for PayPal button:', amount);
      return
    }

    console.log('Attempting to render PayPal button...');
    
    // Cleanup any existing buttons first
    cleanupPayPalButtons()

    try {
      // Render PayPal buttons
      const buttons = window.paypal!.Buttons({
        // Create order function
        createOrder: async (): Promise<string> => {
          try {
            setIsProcessing(true)
            console.log('Creating PayPal order...', stableProps)

            const response = await PayPalAPI.createOrder(stableProps.amount, stableProps.currency, stableProps.description)
            
            if (!response.success || !response.order_id) {
              throw new Error(response.error || 'Failed to create order')
            }

            console.log('Order created successfully:', response.order_id)
            return response.order_id
          } catch (error: any) {
            console.error('Error creating order:', error)
            setIsProcessing(false)
            onError?.(error)
            throw error
          }
        },

        // Approve order function
        onApprove: async (data: PayPalOrderData): Promise<void> => {
          try {
            console.log('PayPal approval received:', data.orderID)

            const response = await PayPalAPI.captureOrder(data.orderID)
            
            if (!response.success) {
              throw new Error(response.error || 'Failed to capture payment')
            }

            console.log('Payment captured successfully:', response)
            setIsProcessing(false)
            onSuccess?.(response)
          } catch (error: any) {
            console.error('Error capturing payment:', error)
            setIsProcessing(false)
            onError?.(error)
          }
        },

        // Error handler
        onError: (error: Error): void => {
          console.error('PayPal button error:', error)
          setIsProcessing(false)
          onError?.(error)
        },

        // Cancel handler
        onCancel: (): void => {
          console.log('PayPal payment cancelled')
          setIsProcessing(false)
          onCancel?.()
        },

        // Button styling - only PayPal button (card funding disabled at SDK level)
        style: {
          layout: 'horizontal',
          color: 'blue',
          shape: 'rect',
          label: 'paypal',
          tagline: false,
          height: 55,
        },
      })

        // Store buttons instance
        buttonsInstanceRef.current = buttons

        // Render buttons to the container
        if (paypalRef.current) {
          console.log('Rendering PayPal buttons to container...');
          buttons.render(paypalRef.current).then(() => {
            setButtonRendered(true)
            console.log('PayPal buttons rendered successfully in', navigator.userAgent.includes('Edg') ? 'Microsoft Edge' : 'browser')
          }).catch((error: Error) => {
            console.error('Error rendering PayPal buttons:', error)
            console.error('Browser info:', navigator.userAgent)
            // Filter out zoid and initialization errors from user alerts
            if (error.message && 
                !error.message.includes('container element removed') &&
                !error.message.includes('zoid destroyed') &&
                !error.message.includes('destroyed all components')) {
              onError?.(error)
            }
          })
        } else {
          console.error('PayPal container ref is null when trying to render')
        }

      } catch (error: any) {
        console.error('Error setting up PayPal buttons:', error)
        // Filter out zoid and initialization errors from user alerts
        if (error.message && 
            !error.message.includes('container element removed') &&
            !error.message.includes('zoid destroyed') &&
            !error.message.includes('destroyed all components')) {
          onError?.(error)
        }
      }

    // Cleanup on unmount
    return () => {
      cleanupPayPalButtons()
    }
  }, [isLoaded, isMounted, componentKey, isValidAmount, hasClientId])

  // Error states - only show after initial loading
  if (showInitialErrors && !hasClientId) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              PayPal Configuration Error
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>PayPal Client ID is not configured.</p>
              <p className="mt-1">Please create a <code>.env.local</code> file with:</p>
              <p className="mt-1 font-mono text-xs bg-gray-100 p-2 rounded">
                PAYPAL_CLIENT_ID=your_client_id_here
              </p>
              <p className="mt-1">Get your Client ID from <a href="https://developer.paypal.com/" target="_blank" className="text-blue-600 underline">PayPal Developer</a></p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (showInitialErrors && !isValidAmount) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Invalid Amount
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>Please enter a valid amount greater than 0.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (showInitialErrors && sdkError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              PayPal SDK Error
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{sdkError}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="paypal-button-container">
      {/* Loading state */}
      {(isLoading || !isLoaded) && (
        <div className="flex items-center justify-center p-8">
          <div className="loading-spinner mr-3"></div>
          <span className="text-gray-600">Loading PayPal...</span>
        </div>
      )}

      {/* Processing state */}
      {isProcessing && (
        <div className="flex items-center justify-center p-4 bg-blue-50 border border-blue-200 rounded-md mb-4">
          <div className="loading-spinner mr-3"></div>
          <span className="text-blue-700">Processing payment...</span>
        </div>
      )}

      {/* PayPal buttons container */}
      <div 
        key={`paypal-buttons-${componentKey}`}
        ref={paypalRef}
        className={`${(disabled || isProcessing) ? 'opacity-50 pointer-events-none' : ''}`}
        style={{ minHeight: isLoaded ? '55px' : '0' }}
      />

      {/* Payment info */}
      {isLoaded && !isProcessing && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          <p>Secure payment powered by PayPal</p>
          <p className="mt-1">Amount: ${stableProps.amount} {stableProps.currency}</p>
        </div>
      )}
    </div>
  )
}

export default PayPalButton
