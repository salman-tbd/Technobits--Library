"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowLeftIcon,
  DevicePhoneMobileIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  CodeBracketIcon
} from "@heroicons/react/24/outline";

export default function Demos() {
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
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
                <div className="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-800 rounded-xl flex items-center justify-center">
                  <CodeBracketIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Demo Mode</h1>
                  <p className="text-sm text-gray-500">Explore Without Signing Up</p>
                </div>
              </div>
            </div>
            <Link
              href="/signup"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
            >
              Sign Up for Full Access
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div 
          className="space-y-12"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Header */}
          <motion.div className="text-center" variants={itemVariants}>
            <div className="w-24 h-24 bg-gradient-to-br from-gray-600 to-gray-800 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-2xl">
              <span className="text-white text-4xl">👀</span>
            </div>
            <h2 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-6">
              Explore Demo Mode
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get a preview of our integrations without creating an account. 
              For full interactive experience and transaction testing, sign up for free!
            </p>
          </motion.div>

          {/* Demo Cards Grid */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 gap-8"
            variants={containerVariants}
          >
            {/* Authentication Demo */}
            <motion.div 
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300"
              variants={itemVariants}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mb-6">
                <ShieldCheckIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Authentication System</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Secure JWT authentication with Google OAuth 2.0 integration. Features automatic token refresh, 
                HTTP-only cookies, and comprehensive security measures.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  JWT tokens in HTTP-only cookies
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  Google Sign-In integration
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  Password reset functionality
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  reCAPTCHA v3 protection
                </div>
              </div>
              <div className="space-y-3">
                <Link 
                  href="/login"
                  className="block w-full text-center px-6 py-3 border border-green-300 text-green-700 bg-green-50 hover:bg-green-100 font-medium rounded-lg transition-all"
                >
                  Try Login Demo
                </Link>
                <Link 
                  href="/signup"
                  className="block w-full text-center px-6 py-3 border border-transparent text-white bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 font-medium rounded-lg transition-all"
                >
                  Sign Up for Full Access
                </Link>
              </div>
            </motion.div>

            {/* Payment Systems Demo */}
            <motion.div 
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-all duration-300"
              variants={itemVariants}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-600 rounded-2xl flex items-center justify-center mb-6">
                <span className="text-white text-2xl">💳</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Payment Integrations</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Complete payment processing solutions with Google Pay and PayPal integrations. 
                Features real-time transactions, webhooks, and comprehensive analytics.
              </p>
              
              {/* Payment Provider Cards */}
              <div className="space-y-4 mb-6">
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center space-x-3 mb-2">
                    <DevicePhoneMobileIcon className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-gray-900">Google Pay Integration</span>
                  </div>
                  <p className="text-sm text-gray-600">Mobile-first payment with INR support</p>
                </div>
                
                <div className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center space-x-3 mb-2">
                    <GlobeAltIcon className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-gray-900">PayPal Integration</span>
                  </div>
                  <p className="text-sm text-gray-600">Global payments with webhook support</p>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-start space-x-2">
                  <span className="text-yellow-600 text-lg">🔒</span>
                  <div>
                    <p className="text-sm font-medium text-yellow-800">Authentication Required</p>
                    <p className="text-sm text-yellow-700">
                      Payment testing requires an account for security and transaction tracking.
                    </p>
                  </div>
                </div>
              </div>

              <Link 
                href="/signup"
                className="block w-full text-center px-6 py-3 border border-transparent text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 font-medium rounded-lg transition-all"
              >
                Sign Up to Test Payments
              </Link>
            </motion.div>
          </motion.div>

          {/* Technology Stack */}
          <motion.div 
            className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-3xl p-12 text-center"
            variants={itemVariants}
          >
            <h3 className="text-3xl font-bold text-gray-900 mb-8">Built with Modern Technologies</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="space-y-3">
                <div className="text-4xl">⚛️</div>
                <div className="font-semibold text-gray-900">Next.js 14</div>
                <div className="text-sm text-gray-600">App Router + TypeScript</div>
              </div>
              <div className="space-y-3">
                <div className="text-4xl">🐍</div>
                <div className="font-semibold text-gray-900">Django 5.0</div>
                <div className="text-sm text-gray-600">REST Framework + JWT</div>
              </div>
              <div className="space-y-3">
                <div className="text-4xl">🎨</div>
                <div className="font-semibold text-gray-900">Tailwind CSS</div>
                <div className="text-sm text-gray-600">Modern Styling</div>
              </div>
              <div className="space-y-3">
                <div className="text-4xl">🔒</div>
                <div className="font-semibold text-gray-900">Secure APIs</div>
                <div className="text-sm text-gray-600">OAuth + Webhooks</div>
              </div>
            </div>
          </motion.div>

          {/* Call to Action */}
          <motion.div 
            className="text-center bg-white rounded-3xl shadow-lg p-12 border border-gray-100"
            variants={itemVariants}
          >
            <h3 className="text-3xl font-bold text-gray-900 mb-6">Ready for the Full Experience?</h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Create your free account to test payment integrations, view analytics, 
              and explore all features of our modern web integration showcase.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/signup"
                className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all transform hover:scale-105 shadow-lg"
              >
                <span>🚀 Create Free Account</span>
              </Link>
              <Link 
                href="/login"
                className="inline-flex items-center px-8 py-4 border border-gray-300 text-lg font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all shadow-lg"
              >
                Already have an account? Sign In
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
