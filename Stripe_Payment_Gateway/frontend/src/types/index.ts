/**
 * Main types export file
 */

// Export payment types
export * from './payment';

// Re-export commonly used types
export type {
  Transaction,
  PaymentStatus,
  CreatePaymentIntentRequest,
  CreatePaymentIntentResponse,
  CreateCheckoutSessionRequest,
  CreateCheckoutSessionResponse,
  SessionStatusResponse,
  TransactionListResponse,
  TransactionDetailResponse,
  PaymentStatsResponse,
  PaymentFormProps,
  ApiResponse,
} from './payment';

// Export utility functions
export {
  formatCurrency,
  getStatusColor,
  validateAmount,
  SUPPORTED_CURRENCIES,
  DEFAULT_CURRENCY,
  MIN_PAYMENT_AMOUNT,
  MAX_PAYMENT_AMOUNT,
} from './payment';