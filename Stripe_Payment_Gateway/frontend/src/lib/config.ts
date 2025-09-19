/**
 * Simplified application configuration
 */

// Stripe Configuration
export const stripeConfig = {
  publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
};

// API Configuration  
export const apiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
};

// App Configuration
export const appConfig = {
  name: process.env.NEXT_PUBLIC_APP_NAME || 'Stripe Payment Gateway',
  url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
};

// Environment Detection
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';

// Simple validation
export const validateConfig = () => {
  const errors: string[] = [];

  if (!stripeConfig.publishableKey) {
    errors.push('NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY is required');
  }

  if (!stripeConfig.publishableKey.startsWith('pk_')) {
    errors.push('NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY must start with pk_');
  }

  if (errors.length > 0) {
    console.error('Configuration errors:', errors);
    if (isProduction) {
      throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
    }
  }

  return errors.length === 0;
};

// Initialize configuration validation
if (typeof window !== 'undefined') {
  validateConfig();
}

export default {
  stripe: stripeConfig,
  api: apiConfig,
  app: appConfig,
  isDevelopment,
  isProduction,
  validateConfig,
};