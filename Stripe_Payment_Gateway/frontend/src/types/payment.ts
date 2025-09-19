/**
 * Simplified Payment types to match our simple backend
 */

// Payment status enum
export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing', 
  SUCCEEDED = 'succeeded',
  FAILED = 'failed',
  CANCELED = 'canceled'
}

// Simple transaction interface matching our backend model
export interface Transaction {
  id: number;
  transaction_id: string;
  stripe_session_id?: string;
  stripe_payment_intent_id?: string;
  amount: string;
  currency: string;
  status: PaymentStatus;
  description?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  stripe_response: Record<string, any>;
}

// Request interfaces for our simple API
export interface CreatePaymentIntentRequest {
  amount: number;
  currency?: string;
  description?: string;
}

export interface CreatePaymentIntentResponse {
  success: boolean;
  client_secret?: string;
  transaction_id?: string;
  message: string;
  error?: string;
}

export interface CreateCheckoutSessionRequest {
  amount: number;
  currency?: string;
  description?: string;
  success_url?: string;
  cancel_url?: string;
}

export interface CreateCheckoutSessionResponse {
  success: boolean;
  data?: {
    checkout_url: string;
    session_id: string;
    transaction_id: string;
  };
  message: string;
}

export interface SessionStatusResponse {
  success: boolean;
  data?: {
    session_id: string;
    payment_status: string;
    customer_email?: string;
  };
  message: string;
  error?: string;
}

export interface TransactionListResponse {
  success: boolean;
  data?: Transaction[];
  count?: number;
  message: string;
}

export interface TransactionDetailResponse {
  success: boolean;
  data?: Transaction;
  message: string;
}

export interface PaymentStatsResponse {
  success: boolean;
  data?: {
    total_transactions: number;
    successful_transactions: number;
    pending_transactions: number;
    failed_transactions: number;
    successful_amount: string;
    success_rate: number;
  };
  message: string;
  error?: string;
}

// Component prop interfaces
export interface PaymentFormProps {
  amount?: number;
  currency?: string;
  description?: string;
  onSuccess?: (sessionId: string) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
  className?: string;
}

// API response type
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
  error?: string;
  errors?: Record<string, string[]>;
}

// Utility functions
export const formatCurrency = (amount: number | string, currency: string = 'USD'): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
    minimumFractionDigits: 2,
  }).format(numAmount);
};

export const getStatusColor = (status: PaymentStatus): string => {
  const colors: Record<PaymentStatus, string> = {
    [PaymentStatus.PENDING]: 'orange',
    [PaymentStatus.PROCESSING]: 'blue', 
    [PaymentStatus.SUCCEEDED]: 'green',
    [PaymentStatus.FAILED]: 'red',
    [PaymentStatus.CANCELED]: 'gray',
  };
  return colors[status] || 'gray';
};

export const validateAmount = (amount: number): string | null => {
  if (amount < 0.50) {
    return 'Minimum amount is $0.50';
  }
  if (amount > 999999.99) {
    return 'Maximum amount exceeded';
  }
  return null;
};

// Constants
export const SUPPORTED_CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
];

export const DEFAULT_CURRENCY = 'USD';
export const MIN_PAYMENT_AMOUNT = 0.50;
export const MAX_PAYMENT_AMOUNT = 999999.99;