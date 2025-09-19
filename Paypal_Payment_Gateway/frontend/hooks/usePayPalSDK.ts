/**
 * Custom hook to load PayPal SDK dynamically
 */
import { useState, useEffect } from 'react'

interface UsePayPalSDKOptions {
  clientId: string
  currency?: string
  intent?: string
}

interface UsePayPalSDKReturn {
  isLoaded: boolean
  isLoading: boolean
  error: string | null
}

export const usePayPalSDK = (options: UsePayPalSDKOptions): UsePayPalSDKReturn => {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { clientId, currency = 'USD', intent = 'capture' } = options

  useEffect(() => {
    console.log('PayPal SDK hook initialized in', navigator.userAgent.includes('Edg') ? 'Microsoft Edge' : 'browser');
    console.log('Client ID available:', !!clientId);
    
    // Check if PayPal SDK is already loaded
    if (window.paypal) {
      console.log('PayPal SDK already loaded, setting state...');
      setIsLoaded(true)
      return
    }

    // Check if script is already in the DOM
    const existingScript = document.querySelector('script[data-paypal-sdk]')
    if (existingScript) {
      console.log('PayPal script already exists in DOM, waiting for load...');
      return
    }

    if (!clientId) {
      console.error('PayPal Client ID is required but not provided');
      setError('PayPal Client ID is required')
      return
    }

    console.log('Starting PayPal SDK loading...');
    setIsLoading(true)
    setError(null)

    // Create script element
    const script = document.createElement('script')
    script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=${currency}&intent=${intent}&components=buttons&disable-funding=card,credit,paylater,venmo`
    script.setAttribute('data-paypal-sdk', 'true')
    script.async = true

    // Handle script load success
    script.onload = () => {
      console.log('PayPal SDK script loaded successfully');
      // Add additional check to ensure window.paypal is available
      if (window.paypal) {
        setIsLoaded(true)
        setIsLoading(false)
        console.log('PayPal SDK fully loaded and ready in', navigator.userAgent.includes('Edg') ? 'Microsoft Edge' : 'browser')
      } else {
        console.warn('PayPal script loaded but window.paypal not available, retrying...');
        // Add small delay for Edge compatibility
        setTimeout(() => {
          if (window.paypal) {
            setIsLoaded(true)
            setIsLoading(false)
            console.log('PayPal SDK loaded after delay')
          } else {
            setError('PayPal SDK loaded but not accessible')
            setIsLoading(false)
          }
        }, 200);
      }
    }

    // Handle script load error
    script.onerror = (e) => {
      console.error('PayPal SDK script failed to load:', e);
      console.error('Browser:', navigator.userAgent);
      setError('Failed to load PayPal SDK')
      setIsLoading(false)
    }

    // Add script to document
    console.log('Adding PayPal script to document head...');
    console.log('Script URL:', script.src);
    document.head.appendChild(script)

    // Cleanup function
    return () => {
      // Remove script when component unmounts
      const scriptToRemove = document.querySelector('script[data-paypal-sdk]')
      if (scriptToRemove) {
        document.head.removeChild(scriptToRemove)
      }
      
      // Reset PayPal object
      if (window.paypal) {
        delete window.paypal
      }
    }
  }, [clientId, currency, intent])

  return { isLoaded, isLoading, error }
}
