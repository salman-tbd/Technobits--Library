"use client";

import { useAuth } from "../../contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowLeftIcon, 
  ChartBarIcon,
  CreditCardIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ArrowPathIcon 
} from "@heroicons/react/24/outline";
import { usePaymentAnalytics } from "../../hooks/usePaymentAnalytics";

export default function Analytics() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const { analytics, transactions, loading, refetch } = usePaymentAnalytics();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login?redirect=/analytics');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-100">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
              </Link>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <ChartBarIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Analytics Dashboard</h1>
                  <p className="text-sm text-gray-500">Transaction Analytics & Insights</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={refetch}
                disabled={loading}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                title="Refresh data"
              >
                <ArrowPathIcon className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user?.name || user?.email?.split('@')[0]}
                </p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div 
          className="space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Payment Analytics Dashboard</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Track your payment integrations performance and transaction patterns
            </p>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium">Loading payment analytics...</p>
            </div>
          ) : analytics ? (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
                      <CreditCardIcon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Transactions</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.total_transactions}</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-xl flex items-center justify-center">
                      <CurrencyDollarIcon className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Volume</p>
                      <p className="text-2xl font-bold text-gray-900">${analytics.total_amount.toFixed(2)}</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center">
                      <ChartBarIcon className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Success Rate</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.success_rate.toFixed(1)}%</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-orange-200 rounded-xl flex items-center justify-center">
                      <UserGroupIcon className="w-6 h-6 text-orange-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Completed</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.completed_transactions}</p>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Provider Breakdown and Recent Transactions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                >
                  <h3 className="text-xl font-semibold text-gray-900 mb-6">Payment Provider Breakdown</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                          <span className="text-green-600 text-sm font-bold">G</span>
                        </div>
                        <span className="font-medium text-gray-900">Google Pay</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">{analytics.provider_breakdown.google_pay}</p>
                        <p className="text-sm text-gray-500">transactions</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full" 
                        style={{ width: `${(analytics.provider_breakdown.google_pay / analytics.total_transactions) * 100}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                          <span className="text-blue-600 text-sm font-bold">P</span>
                        </div>
                        <span className="font-medium text-gray-900">PayPal</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">{analytics.provider_breakdown.paypal}</p>
                        <p className="text-sm text-gray-500">transactions</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full" 
                        style={{ width: `${(analytics.provider_breakdown.paypal / analytics.total_transactions) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.6 }}
                >
                  <h3 className="text-xl font-semibold text-gray-900 mb-6">Recent Transactions</h3>
                  <div className="space-y-4">
                    {transactions.slice(0, 8).map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            transaction.provider === 'google_pay' ? 'bg-green-100' : 'bg-blue-100'
                          }`}>
                            <span className={`text-sm font-bold ${
                              transaction.provider === 'google_pay' ? 'text-green-600' : 'text-blue-600'
                            }`}>
                              {transaction.provider === 'google_pay' ? 'G' : 'P'}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {transaction.currency === 'INR' ? '₹' : '$'}{transaction.amount}
                            </p>
                            <p className="text-sm text-gray-500">{new Date(transaction.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          transaction.is_completed 
                            ? 'bg-green-100 text-green-800' 
                            : transaction.is_failed
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {transaction.status_display}
                        </span>
                      </div>
                    ))}
                    {transactions.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-gray-500">No transactions yet</p>
                        <p className="text-sm text-gray-400 mt-1">Complete a payment to see transactions here</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>

              {/* Action Buttons */}
              <motion.div 
                className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-2xl p-8 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-4">🚀 Dynamic Analytics Dashboard</h3>
                <p className="text-gray-600 max-w-2xl mx-auto mb-6">
                  This dashboard displays real-time transaction data from your payment integrations.
                  Complete payments below to see your analytics update automatically!
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link 
                    href="/checkout/google-pay"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all"
                  >
                    Test Google Pay →
                  </Link>
                  <Link 
                    href="/checkout/paypal"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
                  >
                    Test PayPal →
                  </Link>
                </div>
              </motion.div>
            </>
          ) : (
            <div className="text-center py-16">
              <p className="text-gray-500 mb-4">Unable to load payment analytics</p>
              <button 
                onClick={refetch}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Retry Loading
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
