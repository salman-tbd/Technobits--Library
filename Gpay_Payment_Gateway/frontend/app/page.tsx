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

export default function Home() {
  const [amount, setAmount] = useState('')
  const [paymentsClient, setPaymentsClient] = useState<any>(null)
  const [canMakePayment, setCanMakePayment] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
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
  const merchantName = process.env.NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_NAME || 'Demo Merchant'

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
          border-radius: 4px;
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
    // Get the current amount value directly from the input
    const currentAmount = (document.querySelector('input[type="number"]') as HTMLInputElement)?.value || ''
    console.log('Button clicked! DOM Amount:', currentAmount, 'State Amount:', amount, 'Type:', typeof currentAmount)
    
    if (!currentAmount || currentAmount.trim() === '' || parseFloat(currentAmount) <= 0) {
      setMessage('Please enter a valid amount')
      console.log('Invalid amount detected. Current:', currentAmount)
      return
    }

    setLoading(true)
    setMessage('')

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
          currencyCode: 'INR'
        }
      }

      const paymentData = await client.loadPaymentData(paymentDataRequest)
      
      // Send payment data to backend
      const response = await fetch('http://localhost:8000/api/process-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: paymentData.paymentMethodData.tokenizationData.token,
          amount: currentAmount
        })
      })

      const result = await response.json()
      
      if (result.status === 'success') {
        setMessage('✅ Payment successful!')
        setAmount('')
        // Also clear the DOM input
        const input = document.querySelector('input[type="number"]') as HTMLInputElement
        if (input) input.value = ''
      } else {
        setMessage(`❌ Payment failed: ${result.message}`)
      }
    } catch (error: any) {
      console.error('Payment error:', error)
      setMessage('❌ Payment was cancelled or failed')
    } finally {
      setLoading(false)
    }
  }

  const handleFallbackPayment = async () => {
    if (!amount) {
      setMessage('Please enter an amount')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      // Simulate Google Pay token for testing
      const mockToken = `test_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      // Send to backend
      const response = await fetch('http://localhost:8000/api/process-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: mockToken,
          amount: amount
        })
      })

      const result = await response.json()
      
      if (result.status === 'success') {
        setMessage('✅ Test payment successful! (Mock Google Pay token used)')
        setAmount('')
      } else {
        setMessage(`❌ Payment failed: ${result.message}`)
      }
    } catch (error: any) {
      console.error('Payment error:', error)
      setMessage('❌ Payment processing failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '450px'
      }}>
        <h1 style={{
          textAlign: 'center',
          marginBottom: '2rem',
          color: '#333'
        }}>
          Google Pay Integration
        </h1>
        
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: 'bold',
            color: '#555'
          }}>
            Amount (INR)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Enter amount"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Debug Info */}
        <div style={{
          marginBottom: '1rem',
          padding: '0.75rem',
          backgroundColor: '#e7f3ff',
          border: '1px solid #b3d7ff',
          borderRadius: '4px',
          fontSize: '0.85rem',
          color: '#0056b3'
        }}>
          <strong>Status:</strong> {debugInfo}
        </div>

        {canMakePayment ? (
          <div>
            <div style={{
              marginBottom: '0.5rem',
              fontSize: '0.9rem',
              color: '#666',
              textAlign: 'center'
            }}>
              Google Pay Button:
            </div>
            <div 
              ref={googlePayButtonRef}
              style={{
                width: '100%',
                minHeight: '50px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                marginBottom: '1rem',
                border: '2px dashed #ddd',
                borderRadius: '4px',
                backgroundColor: '#fafafa'
              }}
            >
              <div style={{ color: '#999', fontSize: '0.9rem' }}>
                Waiting for button...
              </div>
            </div>
            {loading && (
              <div style={{
                textAlign: 'center',
                color: '#666',
                fontSize: '0.9rem'
              }}>
                Processing payment...
              </div>
            )}
          </div>
        ) : (
          <div>
            <button
              onClick={handleFallbackPayment}
              disabled={!amount || loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: !amount || loading ? '#ccc' : '#4285f4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '1rem',
                cursor: !amount || loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                marginBottom: '1rem'
              }}
            >
              {loading ? 'Processing...' : '🅖 Pay with Google Pay (Test Mode)'}
            </button>
            
            <div style={{
              padding: '0.75rem',
              backgroundColor: '#fff3cd',
              border: '1px solid #ffeaa7',
              borderRadius: '4px',
              fontSize: '0.85rem',
              color: '#856404'
            }}>
              <strong>💡 To enable real Google Pay:</strong><br/>
              • Use HTTPS (not HTTP)<br/>
              • Try Chrome/Edge browser<br/>
              • Ensure good internet connection<br/>
              • For now, use Test Mode button above
            </div>
          </div>
        )}

        {message && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem',
            backgroundColor: message.includes('successful') ? '#d4edda' : '#f8d7da',
            border: `1px solid ${message.includes('successful') ? '#c3e6cb' : '#f5c6cb'}`,
            borderRadius: '4px',
            color: message.includes('successful') ? '#155724' : '#721c24'
          }}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}