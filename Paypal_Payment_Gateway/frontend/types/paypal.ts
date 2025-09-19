/**
 * TypeScript definitions for PayPal SDK and API responses
 */

// PayPal SDK types
export interface PayPalOrderData {
  orderID: string
}

export interface PayPalActions {
  order: {
    create: (orderData: PayPalCreateOrderData) => Promise<string>
    capture: (orderID: string) => Promise<PayPalCaptureResult>
  }
  resolve: () => void
  reject: (error: Error) => void
}

export interface PayPalCreateOrderData {
  purchase_units: Array<{
    amount: {
      value: string
      currency_code: string
    }
    description?: string
  }>
  intent: 'CAPTURE'
}

export interface PayPalCaptureResult {
  id: string
  status: string
  purchase_units: Array<{
    reference_id: string
    amount: {
      currency_code: string
      value: string
    }
    payee: {
      email_address: string
      merchant_id: string
    }
    payments: {
      captures: Array<{
        id: string
        status: string
        amount: {
          currency_code: string
          value: string
        }
        final_capture: boolean
        create_time: string
        update_time: string
      }>
    }
  }>
  payer: {
    name: {
      given_name: string
      surname: string
    }
    email_address: string
    payer_id: string
    address: {
      country_code: string
    }
  }
  create_time: string
  update_time: string
  links: Array<{
    href: string
    rel: string
    method: string
  }>
}

// Our API response types
export interface CreateOrderResponse {
  success: boolean
  order_id: string
  amount: string
  currency: string
  error?: string
}

export interface CaptureOrderResponse {
  success: boolean
  message: string
  transaction_id: number
  paypal_order_id: string
  amount: string
  currency: string
  error?: string
}

export interface TransactionStatusResponse {
  success: boolean
  transaction_id: number
  paypal_order_id: string
  amount: string
  currency: string
  status: string
  created_at: string
  completed_at: string | null
  error?: string
}

// PayPal Button component props
export interface PayPalButtonProps {
  amount: string
  currency?: string
  description?: string
  onSuccess?: (details: CaptureOrderResponse) => void
  onError?: (error: Error) => void
  onCancel?: () => void
  disabled?: boolean
}

// PayPal SDK window interface
declare global {
  interface Window {
    paypal?: {
      Buttons: (options: PayPalButtonsOptions) => {
        render: (container: string | HTMLElement) => Promise<void>
        close: () => void
      }
    }
  }
}

export interface PayPalButtonsOptions {
  createOrder: () => Promise<string>
  onApprove: (data: PayPalOrderData, actions: PayPalActions) => Promise<void>
  onError?: (error: Error) => void
  onCancel?: () => void
  style?: {
    layout?: 'vertical' | 'horizontal'
    color?: 'gold' | 'blue' | 'silver' | 'white' | 'black'
    shape?: 'rect' | 'pill'
    label?: 'paypal' | 'checkout' | 'buynow' | 'pay'
    tagline?: boolean
    height?: number
  }
}
