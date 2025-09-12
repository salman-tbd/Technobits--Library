'use client'

import { useState, useEffect, useRef } from 'react'

declare global {
  interface Window {
    google?: {
      payments: {
        api: {
          PaymentsClient: new (options: any) => any
        }
      }
    }
  }
}

interface GooglePayButtonProps {
  amount: string;
  currency?: string;
  onSuccess?: (result: any) => void;
  onError?: (error: any) => void;
  onCancel?: () => void;
  disabled?: boolean;
}

export default function GooglePayButton({
  amount,
  currency = 'INR',
  onSuccess,
  onError,
  onCancel,
  disabled = false
}: GooglePayButtonProps) {
  const [paymentsClient, setPaymentsClient] = useState<any>(null)
  const [canMakePayment, setCanMakePayment] = useState(false)
  const [loading, setLoading] = useState(false)
  const [debugInfo, setDebugInfo] = useState('Initializing...')
  const googlePayButtonRef = useRef<HTMLDivElement>(null)

  // Google Pay Configuration
  const baseRequest = {
    apiVersion: 2,
    apiVersionMinor: 0,
  }

  const allowedCardNetworks = ['VISA', 'MASTERCARD']
  const allowedCardAuthMethods = ['PAN_ONLY', 'CRYPTOGRAM_3DS']

  // Environment variables with fallbacks
  const merchantId = process.env.NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID || 'TEST_MERCHANT_ID_FROM_GOOGLE'
  const environment = process.env.NEXT_PUBLIC_GOOGLE_PAY_ENVIRONMENT || 'TEST'
  const merchantName = process.env.NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_NAME || 'Technobits Directory'

  const tokenizationSpecification = {
    type: 'PAYMENT_GATEWAY',
    parameters: {
      gateway: 'example',
      gatewayMerchantId: merchantId
    },
  }

  const baseCardPaymentMethod = {
    type: 'CARD',
    parameters: {
      allowedAuthMethods: allowedCardAuthMethods,
      allowedCardNetworks: allowedCardNetworks,
    },
  }

  const cardPaymentMethod = {
    ...baseCardPaymentMethod,
    tokenizationSpecification: tokenizationSpecification,
  }

  useEffect(() => {
    const initializeGooglePay = () => {
      if (window.google?.payments?.api) {
        try {
          const client = new window.google.payments.api.PaymentsClient({
            environment: environment as 'TEST' | 'PRODUCTION'
          })
          setPaymentsClient(client)
          setDebugInfo('Google Pay client created, checking availability...')
          
          // Check if Google Pay is available
          const isReadyToPayRequest = {
            ...baseRequest,
            allowedPaymentMethods: [baseCardPaymentMethod]
          }

          client.isReadyToPay(isReadyToPayRequest)
            .then((response: any) => {
              console.log('Google Pay isReadyToPay response:', response)
              if (response.result) {
                setCanMakePayment(true)
                setDebugInfo('✅ Google Pay is ready, creating button...')
                
                // Add a small delay to ensure DOM is ready
                setTimeout(() => {
                  addGooglePayButton(client)
                }, 100)
              } else {
                setDebugInfo('❌ Google Pay not ready - may need HTTPS or supported browser')
              }
            })
            .catch((err: any) => {
              console.error('Error checking Google Pay availability:', err)
              setDebugInfo(`❌ Google Pay error: ${err.message}`)
            })
        } catch (error: any) {
          setDebugInfo(`❌ Failed to create Google Pay client: ${error.message}`)
        }
      }
    }

    // Wait for Google Pay script to load
    const checkGooglePay = () => {
      if (window.google?.payments?.api) {
        setDebugInfo('📦 Google Pay API loaded, initializing...')
        initializeGooglePay()
      } else {
        setDebugInfo('⏳ Waiting for Google Pay API to load...')
        setTimeout(checkGooglePay, 200)
      }
    }
    
    checkGooglePay()
    
    // Timeout fallback
    setTimeout(() => {
      if (!window.google?.payments?.api) {
        setDebugInfo('❌ Google Pay API failed to load - check internet connection')
      }
    }, 10000)
  }, [])

  const addGooglePayButton = (client: any) => {
    if (!googlePayButtonRef.current) {
      console.log('Button ref not available')
      setDebugInfo('❌ Button container not ready')
      return
    }

    console.log('Starting button creation...')
    setDebugInfo('🔧 Creating Google Pay button...')
    
    // Show loading state
    googlePayButtonRef.current.innerHTML = '<div style="color: #999; font-size: 0.9rem; text-align: center;">Creating Google Pay button...</div>'
    
    // Set a timeout for fallback - ALWAYS create fallback after 2 seconds
    const fallbackTimeout = setTimeout(() => {
      console.log('Creating fallback button due to timeout')
      setDebugInfo('⏰ Using fallback button')
      createManualGooglePayButton()
    }, 2000)
    
    try {
      // Try to create official button
      const button = client.createButton({
        onClick: () => {
          console.log('Official button clicked, current amount:', amount)
          onGooglePayButtonClicked(client)
        }
      })
      
      // If we get here, button was created successfully
      clearTimeout(fallbackTimeout)
      googlePayButtonRef.current.innerHTML = ''
      googlePayButtonRef.current.appendChild(button)
      setDebugInfo('✅ Official Google Pay button created!')
      console.log('Official button created successfully')
      
    } catch (error: any) {
      console.error('Button creation error:', error)
      clearTimeout(fallbackTimeout)
      setDebugInfo(`❌ Button error: ${error.message}`)
      createManualGooglePayButton()
    }
  }

  const createManualGooglePayButton = () => {
    if (googlePayButtonRef.current) {
      googlePayButtonRef.current.innerHTML = `
        <button id="manual-gpay-btn" style="
          background: #4285f4;
          color: white;
          border: none;
          border-radius: 8px;
          padding: 12px 24px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          width: 100%;
          min-height: 48px;
          transition: background 0.2s;
        " onmouseover="this.style.background='#3367d6'" onmouseout="this.style.background='#4285f4'">
          🅖 Pay with Google Pay
        </button>
      `
      
      // Add click event listener
      const button = googlePayButtonRef.current.querySelector('#manual-gpay-btn')
      if (button) {
        button.addEventListener('click', () => {
          console.log('Manual button clicked, current amount:', amount)
          onGooglePayButtonClicked(paymentsClient)
        })
      }
      
      setDebugInfo('✅ Manual Google Pay button created!')
    }
  }

  const onGooglePayButtonClicked = async (client: any) => {
    // Get the current amount value
    const currentAmount = amount || '0'
    console.log('Button clicked! Amount:', currentAmount)
    
    if (!currentAmount || currentAmount.trim() === '' || parseFloat(currentAmount) <= 0) {
      onError?.(new Error('Please enter a valid amount'))
      console.log('Invalid amount detected. Current:', currentAmount)
      return
    }

    setLoading(true)

    try {
      const paymentDataRequest = {
        ...baseRequest,
        allowedPaymentMethods: [cardPaymentMethod],
        merchantInfo: {
          merchantId: merchantId,
          merchantName: merchantName
        },
        transactionInfo: {
          totalPriceStatus: 'FINAL',
          totalPrice: currentAmount,
          currencyCode: currency
        }
      }

      const paymentData = await client.loadPaymentData(paymentDataRequest)
      
      // Send payment data to backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/payments/google-pay/process/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          token: paymentData.paymentMethodData.tokenizationData.token,
          amount: currentAmount,
          currency: currency
        })
      })

      const result = await response.json()
      
      if (result.status === 'success' || response.ok) {
        onSuccess?.(result)
      } else {
        onError?.(new Error(result.message || 'Payment failed'))
      }
    } catch (error: any) {
      console.error('Payment error:', error)
      if (error.message && error.message.includes('CANCELED')) {
        onCancel?.()
      } else {
        onError?.(error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleFallbackPayment = async () => {
    if (!amount) {
      onError?.(new Error('Please enter an amount'))
      return
    }

    setLoading(true)

    try {
      // Simulate Google Pay token for testing
      const mockToken = `test_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      // Send to backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/payments/google-pay/process/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          token: mockToken,
          amount: amount,
          currency: currency
        })
      })

      const result = await response.json()
      
      if (result.status === 'success' || response.ok) {
        onSuccess?.(result)
      } else {
        onError?.(new Error(result.message || 'Payment failed'))
      }
    } catch (error: any) {
      console.error('Payment error:', error)
      onError?.(error)
    } finally {
      setLoading(false)
    }
  }

  // Error states
  if (!merchantId || merchantId.includes('TEST_MERCHANT_ID_FROM_GOOGLE')) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Google Pay Configuration Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>Google Pay Merchant ID is not configured.</p>
              <p className="mt-1">Please check your environment variables.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!amount || parseFloat(amount) <= 0) {
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

  return (
    <div className="google-pay-container">
      {/* Debug Info */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
        <strong>Status:</strong> {debugInfo}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center p-4 bg-blue-50 border border-blue-200 rounded-lg mb-4">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-3"></div>
          <span className="text-blue-700">Processing payment...</span>
        </div>
      )}

      {canMakePayment ? (
        <div>
          <div className="mb-2 text-sm text-gray-600 text-center">
            Google Pay Button:
          </div>
          <div 
            ref={googlePayButtonRef}
            className={`w-full min-h-[48px] flex items-center justify-center rounded-lg ${
              (disabled || loading) ? 'opacity-50 pointer-events-none' : ''
            }`}
            style={{ minHeight: '48px' }}
          >
            <div className="text-gray-500 text-sm">Waiting for button...</div>
          </div>
        </div>
      ) : (
        <div>
          <button
            onClick={handleFallbackPayment}
            disabled={!amount || loading || disabled}
            className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Processing...
              </>
            ) : (
              <>🅖 Pay with Google Pay (Test Mode)</>
            )}
          </button>
          
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
            <strong>💡 To enable real Google Pay:</strong><br/>
            • Use HTTPS (not HTTP)<br/>
            • Try Chrome/Edge browser<br/>
            • Ensure good internet connection<br/>
            • For now, use Test Mode button above
          </div>
        </div>
      )}

      {/* Payment info */}
      {!loading && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          <p>Secure payment powered by Google Pay</p>
          <p className="mt-1">Amount: {currency === 'INR' ? '₹' : '$'}{amount} {currency}</p>
        </div>
      )}

      {/* Load Google Pay Script */}
      <script src="https://pay.google.com/gp/p/js/pay.js" async></script>
    </div>
  )
}
