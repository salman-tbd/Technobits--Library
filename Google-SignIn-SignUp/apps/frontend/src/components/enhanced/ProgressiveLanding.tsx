"use client";

import Link from "next/link";
import { useAuth } from "../../contexts/AuthContext";
import { useState } from "react";
import { motion } from "framer-motion";
import { 
  CreditCardIcon, 
  ShieldCheckIcon, 
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  ChartBarIcon,
  CodeBracketIcon
} from "@heroicons/react/24/outline";

export default function ProgressiveLanding() {
  const { user, isAuthenticated, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Enhanced Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <motion.div 
              className="flex items-center space-x-3"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">🚀</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Technobits Directory
                </h1>
                <p className="text-sm text-gray-500">Modern Web Integration Showcase</p>
              </div>
            </motion.div>
            
            {isAuthenticated && user && (
              <motion.div 
                className="flex items-center space-x-4"
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || user?.email?.split('@')[0] || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoggingOut ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Signing Out...
                    </>
                  ) : (
                    'Sign Out'
                  )}
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {isAuthenticated && user ? (
          // Authenticated Progressive Experience
          <motion.div 
            className="space-y-12"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Welcome Section */}
            <motion.div className="text-center" variants={itemVariants}>
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-white text-3xl">🎉</span>
              </div>
              <h2 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-4">
                Welcome to the Full Experience!
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                You're authenticated and ready to explore all integrations. Choose your next adventure!
              </p>
            </motion.div>

            {/* Progressive Action Cards */}
            <motion.div 
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              variants={containerVariants}
            >
              <motion.div variants={itemVariants}>
                <Link href="/checkout/google-pay" className="block group">
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300 group-hover:border-green-200">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                      <DevicePhoneMobileIcon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">Try Google Pay</h3>
                    <p className="text-gray-600 mb-4">Experience mobile-first payment processing with Google Pay integration.</p>
                    <div className="text-sm text-green-600 font-medium">Test Mobile Payments →</div>
                  </div>
                </Link>
              </motion.div>

              <motion.div variants={itemVariants}>
                <Link href="/checkout/paypal" className="block group">
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300 group-hover:border-blue-200">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                      <GlobeAltIcon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">Try PayPal</h3>
                    <p className="text-gray-600 mb-4">Explore global payment processing with PayPal's complete API.</p>
                    <div className="text-sm text-blue-600 font-medium">Test Global Payments →</div>
                  </div>
                </Link>
              </motion.div>

              <motion.div variants={itemVariants}>
                {isAuthenticated ? (
                  <Link href="/analytics" className="block group">
                    <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300 group-hover:border-purple-200">
                      <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                        <ChartBarIcon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">View Analytics</h3>
                      <p className="text-gray-600 mb-4">Analyze your transaction history and payment patterns.</p>
                      <div className="text-sm text-purple-600 font-medium">View Dashboard →</div>
                    </div>
                  </Link>
                ) : (
                  <Link href="/login" className="block group">
                    <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300 group-hover:border-purple-200">
                      <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                        <ChartBarIcon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">View Analytics</h3>
                      <p className="text-gray-600 mb-4">Sign in to analyze your transaction history and payment patterns.</p>
                      <div className="text-sm text-purple-600 font-medium">Sign In to View →</div>
                    </div>
                  </Link>
                )}
              </motion.div>
            </motion.div>

            {/* User Account Dashboard */}
            <motion.div 
              id="account-dashboard"
              className="bg-white/80 backdrop-blur rounded-2xl shadow-lg p-8 max-w-4xl mx-auto border border-white/20"
              variants={itemVariants}
            >
              <h3 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                <span className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center mr-3">
                  👤
                </span>
                Your Account Dashboard
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-3 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">Email Address</span>
                    <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded-lg">
                      {user?.email || 'Not provided'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">Display Name</span>
                    <span className="text-gray-900">
                      {user?.name || user?.email?.split('@')[0] || 'Not provided'}
                    </span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-3 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">User ID</span>
                    <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded-lg">
                      {user?.id || 'Not provided'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-3">
                    <span className="text-gray-600 font-medium">Account Status</span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      Active & Verified
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        ) : (
          // Enhanced Landing for Non-Authenticated Users
          <motion.div 
            className="space-y-16"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Hero Section */}
            <motion.div className="text-center" variants={itemVariants}>
              <div className="w-32 h-32 bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-2xl">
                <span className="text-white text-5xl">🚀</span>
              </div>
              <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-6">
                Technobits Directory
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed">
                Explore modern web integrations with{" "}
                <span className="text-blue-600 font-semibold">Google Auth</span>,{" "}
                <span className="text-green-600 font-semibold">Google Pay</span>, and{" "}
                <span className="text-blue-700 font-semibold">PayPal</span> - 
                all production-ready implementations built with Next.js 14 and Django 5.0
              </p>
              
              {/* Progressive CTA */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
                <Link 
                  href="/signup" 
                  className="group inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all transform hover:scale-105 shadow-lg"
                >
                  <span>🚀 Start Progressive Demo</span>
                  <motion.span 
                    className="ml-2"
                    animate={{ x: [0, 4, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    →
                  </motion.span>
                </Link>
                <Link 
                  href="/login" 
                  className="inline-flex items-center px-8 py-4 border border-gray-300 text-lg font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all shadow-lg"
                >
                  Already have an account? Sign In
                </Link>
              </div>

              {/* Demo Mode Option */}
              <motion.div 
                className="inline-flex items-center px-6 py-3 bg-white/70 backdrop-blur border border-gray-200 rounded-xl shadow-sm"
                variants={itemVariants}
              >
                <span className="text-gray-600 mr-2">Want to explore without signing up?</span>
                <Link 
                  href="/demos" 
                  className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  Try Demo Mode →
                </Link>
              </motion.div>
            </motion.div>

            {/* Enhanced Features Grid */}
            <motion.div 
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
              variants={containerVariants}
            >
              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <ShieldCheckIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Secure Authentication</h3>
                <p className="text-gray-600 leading-relaxed">
                  JWT tokens in HTTP-only cookies with automatic refresh, Google OAuth 2.0, and comprehensive security features.
                </p>
              </motion.div>
              
              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <GlobeAltIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Google Sign-In</h3>
                <p className="text-gray-600 leading-relaxed">
                  One-click authentication with Google Identity Services and server-side credential verification.
                </p>
              </motion.div>
              
              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <CodeBracketIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Modern UI</h3>
                <p className="text-gray-600 leading-relaxed">
                  Beautiful, responsive interface built with Tailwind CSS, Framer Motion, and modern React patterns.
                </p>
              </motion.div>

              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <DevicePhoneMobileIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Google Pay Integration</h3>
                <p className="text-gray-600 leading-relaxed">
                  Mobile-first payment experience with Google Pay API, supporting INR and test environments.
                </p>
              </motion.div>

              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <CreditCardIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">PayPal Integration</h3>
                <p className="text-gray-600 leading-relaxed">
                  Complete PayPal Orders API v2 integration with webhooks, transaction management, and global support.
                </p>
              </motion.div>

              <motion.div className="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 hover:shadow-xl transition-all duration-300" variants={itemVariants}>
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <ChartBarIcon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Transaction Analytics</h3>
                <p className="text-gray-600 leading-relaxed">
                  Real-time transaction tracking, payment history, and comprehensive analytics dashboard.
                </p>
              </motion.div>
            </motion.div>

            {/* Technology Stack */}
            <motion.div 
              className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-3xl p-12 text-center"
              variants={itemVariants}
            >
              <h3 className="text-3xl font-bold text-gray-900 mb-8">Built with Modern Technologies</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                <div className="space-y-2">
                  <div className="text-3xl">⚛️</div>
                  <div className="font-semibold text-gray-900">Next.js 14</div>
                  <div className="text-sm text-gray-600">App Router + TypeScript</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl">🐍</div>
                  <div className="font-semibold text-gray-900">Django 5.0</div>
                  <div className="text-sm text-gray-600">REST Framework + JWT</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl">🎨</div>
                  <div className="font-semibold text-gray-900">Tailwind CSS</div>
                  <div className="text-sm text-gray-600">Modern Styling</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl">🔒</div>
                  <div className="font-semibold text-gray-900">Secure APIs</div>
                  <div className="text-sm text-gray-600">OAuth + Webhooks</div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
