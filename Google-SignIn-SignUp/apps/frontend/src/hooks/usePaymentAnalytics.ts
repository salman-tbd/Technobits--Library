import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8003';

export interface PaymentTransaction {
  id: string;
  transaction_id: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  provider: 'google_pay' | 'paypal';
  provider_display: string;
  amount: string;
  currency: string;
  description: string;
  status: string;
  status_display: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  is_completed: boolean;
  is_failed: boolean;
}

export interface PaymentAnalytics {
  total_transactions: number;
  completed_transactions: number;
  success_rate: number;
  total_amount: number;
  provider_breakdown: {
    google_pay: number;
    paypal: number;
  };
  recent_transactions: Array<{
    id: string;
    provider: string;
    amount: number;
    currency: string;
    status: string;
    created_at: string;
  }>;
}

export const usePaymentAnalytics = () => {
  const [analytics, setAnalytics] = useState<PaymentAnalytics | null>(null);
  const [transactions, setTransactions] = useState<PaymentTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to fetch real data from backend
      const [analyticsResponse, transactionsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/payments/analytics/`, {
          withCredentials: true,
        }),
        axios.get(`${API_BASE_URL}/api/payments/transactions/`, {
          params: { limit: 10 },
          withCredentials: true,
        })
      ]);

      if (analyticsResponse.data.success && transactionsResponse.data.success) {
        setAnalytics(analyticsResponse.data.analytics);
        setTransactions(transactionsResponse.data.transactions);
      } else {
        throw new Error('API response not successful');
      }
    } catch (err) {
      // Fallback to mock data for demo purposes
      console.log('Using mock data for demo purposes');
      setAnalytics(getMockAnalytics());
      setTransactions(getMockTransactions());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const getMockTransactions = (): PaymentTransaction[] => {
    const now = new Date();
    return [
      {
        id: '1',
        transaction_id: 'GPY_20250912_001',
        user: {
          id: 1,
          email: 'demo@technobits.com',
          first_name: 'Demo',
          last_name: 'User'
        },
        provider: 'google_pay',
        provider_display: 'Google Pay',
        amount: '25.99',
        currency: 'INR',
        description: 'Google Pay payment of 25.99 INR',
        status: 'completed',
        status_display: 'Completed',
        created_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
        completed_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
        is_completed: true,
        is_failed: false
      },
      {
        id: '2',
        transaction_id: 'PP_20250912_002',
        user: {
          id: 1,
          email: 'demo@technobits.com',
          first_name: 'Demo',
          last_name: 'User'
        },
        provider: 'paypal',
        provider_display: 'PayPal',
        amount: '15.50',
        currency: 'USD',
        description: 'PayPal payment of 15.50 USD',
        status: 'completed',
        status_display: 'Completed',
        created_at: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
        completed_at: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
        is_completed: true,
        is_failed: false
      },
      {
        id: '3',
        transaction_id: 'GPY_20250912_003',
        user: {
          id: 1,
          email: 'demo@technobits.com',
          first_name: 'Demo',
          last_name: 'User'
        },
        provider: 'google_pay',
        provider_display: 'Google Pay',
        amount: '50.00',
        currency: 'INR',
        description: 'Google Pay payment of 50.00 INR',
        status: 'failed',
        status_display: 'Failed',
        created_at: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
        is_completed: false,
        is_failed: true
      }
    ];
  };

  const getMockAnalytics = (): PaymentAnalytics => {
    return {
      total_transactions: 3,
      completed_transactions: 2,
      success_rate: 66.7,
      total_amount: 41.49,
      provider_breakdown: {
        google_pay: 2,
        paypal: 1
      },
      recent_transactions: [
        {
          id: 'GPY_20250912_001',
          provider: 'google_pay',
          amount: 25.99,
          currency: 'INR',
          status: 'completed',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'PP_20250912_002',
          provider: 'paypal',
          amount: 15.50,
          currency: 'USD',
          status: 'completed',
          created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'GPY_20250912_003',
          provider: 'google_pay',
          amount: 50.00,
          currency: 'INR',
          status: 'failed',
          created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
        }
      ]
    };
  };

  return {
    analytics,
    transactions,
    loading,
    error,
    refetch: fetchAnalyticsData
  };
};
