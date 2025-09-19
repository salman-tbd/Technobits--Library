/**
 * Simplified Payment API client to match our backend endpoints
 */

import { api } from './client';
import {
  CreatePaymentIntentRequest,
  CreatePaymentIntentResponse,
  CreateCheckoutSessionRequest,
  CreateCheckoutSessionResponse,
  SessionStatusResponse,
  TransactionListResponse,
  TransactionDetailResponse,
  PaymentStatsResponse,
} from '@/types/payment';

/**
 * Payment API client
 */
export const paymentsApi = {
  /**
   * Create a Stripe Payment Intent
   */
  createPaymentIntent: async (
    data: CreatePaymentIntentRequest
  ): Promise<CreatePaymentIntentResponse> => {
    const response = await api.post<CreatePaymentIntentResponse>(
      '/create-payment-intent/',
      data
    );
    
    return response;
  },

  /**
   * Create a Stripe Checkout Session
   */
  createCheckoutSession: async (
    data: CreateCheckoutSessionRequest
  ): Promise<CreateCheckoutSessionResponse> => {
    const response = await api.post<any>(
      '/create-checkout-session/',
      data
    );
    
    return {
      success: response.success,
      data: response.checkout_url ? {
        checkout_url: response.checkout_url,
        session_id: response.session_id,
        transaction_id: response.transaction_id,
      } : undefined,
      message: response.message,
    };
  },

  /**
   * Get session status from Stripe
   */
  getSessionStatus: async (sessionId: string): Promise<SessionStatusResponse> => {
    const response = await api.get<SessionStatusResponse>(
      `/session-status/?session_id=${sessionId}`
    );
    
    return response;
  },

  /**
   * Get list of transactions
   */
  getTransactions: async (): Promise<TransactionListResponse> => {
    const response = await api.get<TransactionListResponse>('/');
    
    return response;
  },

  /**
   * Get transaction details by ID
   */
  getTransaction: async (transactionId: number): Promise<TransactionDetailResponse> => {
    const response = await api.get<TransactionDetailResponse>(`/${transactionId}/`);
    
    return response;
  },

  /**
   * Get payment statistics
   */
  getPaymentStats: async (): Promise<PaymentStatsResponse> => {
    const response = await api.get<PaymentStatsResponse>('/stats/');
    
    return response;
  },
};

/**
 * Payment utility functions
 */
export const paymentUtils = {
  /**
   * Format currency amount
   */
  formatAmount: (amount: number | string, currency: string = 'USD'): string => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
    }).format(numAmount);
  },

  /**
   * Validate payment amount
   */
  validateAmount: (amount: number): string | null => {
    if (amount < 0.50) {
      return 'Minimum amount is $0.50';
    }
    if (amount > 999999.99) {
      return 'Maximum amount exceeded';
    }
    return null;
  },

  /**
   * Get payment status color for UI
   */
  getStatusColor: (status: string): string => {
    const colors: Record<string, string> = {
      pending: 'orange',
      processing: 'blue',
      succeeded: 'green',
      failed: 'red',
      canceled: 'gray',
    };
    return colors[status] || 'gray';
  },

  /**
   * Generate a simple reference ID
   */
  generateReference: (): string => {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `PAY-${timestamp}-${random}`.toUpperCase();
  },
};

// Default export
export default paymentsApi;