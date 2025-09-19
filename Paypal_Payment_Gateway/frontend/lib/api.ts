/**
 * API service for communicating with Django backend
 */
import axios, { AxiosResponse } from 'axios'
import { CreateOrderResponse, CaptureOrderResponse, TransactionStatusResponse } from '@/types/paypal'

const API_BASE_URL = process.env.DJANGO_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    
    // Handle specific error cases
    if (error.response?.status === 404) {
      throw new Error('Resource not found')
    } else if (error.response?.status === 500) {
      throw new Error('Internal server error')
    } else if (error.code === 'ECONNREFUSED') {
      throw new Error('Unable to connect to server. Please check if Django is running.')
    }
    
    throw error
  }
)

export class PayPalAPI {
  /**
   * Create a PayPal order
   */
  static async createOrder(
    amount: string,
    currency: string = 'USD',
    description: string = ''
  ): Promise<CreateOrderResponse> {
    try {
      const response: AxiosResponse<CreateOrderResponse> = await apiClient.post(
        '/paypal/create-order/',
        {
          amount,
          currency,
          description,
        }
      )
      
      return response.data
    } catch (error: any) {
      console.error('Create order error:', error)
      throw new Error(
        error.response?.data?.error || 
        error.message || 
        'Failed to create PayPal order'
      )
    }
  }

  /**
   * Capture a PayPal order after approval
   */
  static async captureOrder(orderID: string): Promise<CaptureOrderResponse> {
    try {
      const response: AxiosResponse<CaptureOrderResponse> = await apiClient.post(
        '/paypal/capture-order/',
        {
          order_id: orderID,
        }
      )
      
      return response.data
    } catch (error: any) {
      console.error('Capture order error:', error)
      throw new Error(
        error.response?.data?.error || 
        error.message || 
        'Failed to capture PayPal order'
      )
    }
  }

  /**
   * Get transaction status
   */
  static async getTransactionStatus(orderID: string): Promise<TransactionStatusResponse> {
    try {
      const response: AxiosResponse<TransactionStatusResponse> = await apiClient.get(
        `/paypal/transaction-status/${orderID}/`
      )
      
      return response.data
    } catch (error: any) {
      console.error('Get transaction status error:', error)
      throw new Error(
        error.response?.data?.error || 
        error.message || 
        'Failed to get transaction status'
      )
    }
  }
}

export default PayPalAPI
