/**
 * Simplified API client for Stripe Payment Gateway
 * No authentication required - matches our simple backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
const REQUEST_TIMEOUT = 30000; // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Response: ${response.status}`, response.data);
    }
    return response;
  },
  (error) => {
    // Transform error to standard format
    const apiError = {
      message: error.response?.data?.message || error.message || 'An error occurred',
      status: error.response?.status || 500,
      error: error.response?.data?.error,
      errors: error.response?.data?.errors,
    };

    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', apiError);
    }

    return Promise.reject(apiError);
  }
);

// Generic API request function - returns raw response data
async function makeRequest<T = any>(
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  try {
    const response = await apiClient.request<T>({
      method,
      url,
      data,
      ...config,
    });

    return response.data;
  } catch (error) {
    throw error;
  }
}

// Convenience methods
export const api = {
  // GET request
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    makeRequest<T>('GET', url, undefined, config),

  // POST request  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    makeRequest<T>('POST', url, data, config),

  // PUT request
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    makeRequest<T>('PUT', url, data, config),

  // PATCH request
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    makeRequest<T>('PATCH', url, data, config),

  // DELETE request
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    makeRequest<T>('DELETE', url, undefined, config),
};

// Export the configured axios instance
export { apiClient };

// Default export
export default api;