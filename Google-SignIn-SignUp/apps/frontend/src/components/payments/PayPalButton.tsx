'use client'

import React, { useEffect, useRef, useState, useMemo } from 'react'

interface PayPalButtonProps {
  amount: string;
  currency?: string;
  description?: string;
  onSuccess?: (details: any) => void;
  onError?: (error: any) => void;
  onCancel?: () => void;
  disabled?: boolean;
}

declare global {
  interface Window {
    paypal?: any;
  }
}

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
  const [isLoaded, setIsLoaded] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [paymentCompleted, setPaymentCompleted] = useState(false)

  // Get PayPal Client ID from environment
  const clientId = process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID || process.env.PAYPAL_CLIENT_ID

  // Validate props
  const isValidAmount = amount && parseFloat(amount) > 0
  const hasClientId = !!clientId && !clientId.includes('your-client-id')

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
        console.debug('PayPal cleanup error (expected):', error?.message)
      }
      buttonsInstanceRef.current = null
    }
    if (paypalRef.current) {
      try {
        paypalRef.current.innerHTML = ''
      } catch (error: any) {
        console.debug('DOM cleanup error (expected):', error?.message)
      }
    }
    setButtonRendered(false)
  }

  // Track last rendered values to prevent unnecessary re-renders
  const lastRenderedValues = useRef({ amount: '', description: '' })
  
  // Only trigger re-render when values actually change
  useEffect(() => {
    if (stableProps.amount !== lastRenderedValues.current.amount || 
        stableProps.description !== lastRenderedValues.current.description) {
      
      lastRenderedValues.current = {
        amount: stableProps.amount,
        description: stableProps.description
      }
      
      setComponentKey(prev => prev + 1)
      cleanupPayPalButtons()
    }
  }, [stableProps.amount, stableProps.description])

  // Load PayPal SDK
  useEffect(() => {
    if (!hasClientId) {
      setError('PayPal Client ID not configured')
      setIsLoading(false)
      return
    }

    const loadPayPalSDK = () => {
      if (window.paypal) {
        setIsLoaded(true)
        setIsLoading(false)
        return
      }

      const script = document.createElement('script')
      script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=${currency}&disable-funding=credit,card`
      script.async = true
      script.onload = () => {
        console.log('PayPal SDK loaded successfully')
        setIsLoaded(true)
        setIsLoading(false)
      }
      script.onerror = () => {
        console.error('Failed to load PayPal SDK')
        setError('Failed to load PayPal SDK')
        setIsLoading(false)
      }
      
      document.head.appendChild(script)
    }

    loadPayPalSDK()
  }, [clientId, currency, hasClientId])

  // Mount component
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMounted(true)
      console.log('PayPal component mounted and ready')
    }, 150)
    
    return () => clearTimeout(timer)
  }, [])

  // Render PayPal buttons
  useEffect(() => {
    if (!isMounted || !isLoaded || !window.paypal || !isValidAmount || !hasClientId) {
      console.log('PayPal button not ready:', { isMounted, isLoaded, hasPayPal: !!window.paypal, isValidAmount, hasClientId })
      return
    }

    if (!paypalRef.current) {
      console.log('PayPal container ref not available')
      return
    }

    if (!amount || parseFloat(amount) <= 0) {
      console.log('Invalid amount for PayPal button:', amount)
      return
    }

    console.log('Attempting to render PayPal button...')
    
    cleanupPayPalButtons()

    try {
      const buttons = window.paypal!.Buttons({
        createOrder: async (): Promise<string> => {
          try {
            // Prevent double-click by checking if already processing
            if (isProcessing || paymentCompleted) {
              console.log('Payment already processing or completed, preventing duplicate')
              throw new Error('Payment already in progress')
            }
            
            setIsProcessing(true)
            console.log('Creating PayPal order...', stableProps)

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/payments/paypal/create-order/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              body: JSON.stringify({
                amount: stableProps.amount,
                currency: stableProps.currency,
                description: stableProps.description
              })
            })
            
            const data = await response.json()

            if (!response.ok || !data.success || !data.order_id) {
              throw new Error(data.error || 'Failed to create order')
            }

            console.log('Order created successfully:', data.order_id)
            return data.order_id
          } catch (error: any) {
            console.error('Error creating order:', error)
            setIsProcessing(false)
            onError?.(error)
            throw error
          }
        },

        onApprove: async (data: any): Promise<void> => {
          try {
            console.log('PayPal approval received:', data.orderID)

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/payments/paypal/capture-order/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              body: JSON.stringify({
                order_id: data.orderID
              })
            })
            
            const result = await response.json()

            if (!response.ok || !result.success) {
              throw new Error(result.error || 'Failed to capture payment')
            }

            console.log('Payment captured successfully:', result)
            setIsProcessing(false)
            setPaymentCompleted(true)
            
            // Hide PayPal button after successful payment to prevent interference
            setTimeout(() => {
              if (paypalRef.current) {
                paypalRef.current.style.display = 'none'
                paypalRef.current.style.visibility = 'hidden'
                paypalRef.current.style.opacity = '0'
                paypalRef.current.style.pointerEvents = 'none'
              }
            }, 100)
            
            onSuccess?.(result)
          } catch (error: any) {
            console.error('Error capturing payment:', error)
            setIsProcessing(false)
            onError?.(error)
          }
        },

        onError: (error: any): void => {
          console.error('PayPal button error:', error)
          setIsProcessing(false)
          onError?.(error)
        },

        onCancel: (): void => {
          console.log('PayPal payment cancelled')
          setIsProcessing(false)
          onCancel?.()
        },

        style: {
          layout: 'horizontal',
          color: 'blue',
          shape: 'rect',
          label: 'paypal',
          tagline: false,
          height: 55,
        },
      })

      buttonsInstanceRef.current = buttons

      if (paypalRef.current) {
        console.log('Rendering PayPal buttons to container...')
        buttons.render(paypalRef.current).then(() => {
          setButtonRendered(true)
          console.log('PayPal buttons rendered successfully')
        }).catch((error: Error) => {
          console.error('Error rendering PayPal buttons:', error)
          if (error.message && 
              !error.message.includes('container element removed') &&
              !error.message.includes('zoid destroyed') &&
              !error.message.includes('destroyed all components')) {
            setError(error.message)
            onError?.(error)
          }
        })
      } else {
        console.error('PayPal container ref is null when trying to render')
      }

    } catch (error: any) {
      console.error('Error setting up PayPal buttons:', error)
      if (error.message && 
          !error.message.includes('container element removed') &&
          !error.message.includes('zoid destroyed') &&
          !error.message.includes('destroyed all components')) {
        setError(error.message)
        onError?.(error)
      }
    }

    return () => {
      cleanupPayPalButtons()
    }
  }, [isLoaded, isMounted, componentKey, isValidAmount, hasClientId])

  // Error states
  if (!hasClientId) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">PayPal Configuration Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>PayPal Client ID is not configured.</p>
              <p className="mt-1">Please check your environment variables.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!isValidAmount) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Invalid Amount</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>Please enter a valid amount greater than 0.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">PayPal Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
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
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-3"></div>
          <span className="text-gray-600">Loading PayPal...</span>
        </div>
      )}

      {/* Processing state */}
      {isProcessing && !paymentCompleted && (
        <div className="flex items-center justify-center p-4 bg-blue-50 border border-blue-200 rounded-lg mb-4">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-3"></div>
          <span className="text-blue-700">Processing payment...</span>
        </div>
      )}

      {/* Payment completed state */}
      {paymentCompleted && (
        <div className="flex items-center justify-center p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
          <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3">
            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
            </svg>
          </div>
          <span className="text-green-700 font-medium">Payment completed successfully!</span>
        </div>
      )}

      {/* PayPal buttons container */}
      <div 
        key={`paypal-buttons-${componentKey}`}
        ref={paypalRef}
        className={`transition-all duration-300 ${
          (disabled || isProcessing || paymentCompleted) ? 'opacity-50 pointer-events-none' : ''
        } ${paymentCompleted ? 'hidden' : ''}`}
        style={{ 
          minHeight: isLoaded ? '55px' : '0',
          display: paymentCompleted ? 'none' : 'block',
          visibility: paymentCompleted ? 'hidden' : 'visible'
        }}
      />

      {/* Payment info */}
      {isLoaded && !isProcessing && !paymentCompleted && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          <p>Secure payment powered by PayPal</p>
          <p className="mt-1">Amount: ${stableProps.amount} {stableProps.currency}</p>
        </div>
      )}
    </div>
  )
}

export default PayPalButton
