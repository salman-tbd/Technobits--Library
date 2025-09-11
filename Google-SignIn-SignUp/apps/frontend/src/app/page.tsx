"use client";

import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";
import { useState } from "react";

export default function Home() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading your authentication status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🔐</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Auth Demo</h1>
                <p className="text-sm text-gray-500">Secure Authentication System</p>
              </div>
            </div>
            
            {isAuthenticated && user && (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || user?.email?.split('@')[0] || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {isAuthenticated && user ? (
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-white text-3xl">✨</span>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome back!</h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                You&apos;re successfully authenticated and logged into your secure account.
              </p>
            </div>

            {/* User Info Card */}
            <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                <span className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  👤
                </span>
                Account Information
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600 font-medium">Email Address</span>
                  <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded">
                    {user?.email || 'Not provided'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600 font-medium">Display Name</span>
                  <span className="text-gray-900">
                    {user?.name || user?.email?.split('@')[0] || 'Not provided'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="text-gray-600 font-medium">User ID</span>
                  <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded">
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

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                <span className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                  ⚡
                </span>
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <span className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    🔄
                  </span>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Refresh Profile</p>
                    <p className="text-sm text-gray-500">Update account info</p>
                  </div>
                </button>
                <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <span className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                    ⚙️
                  </span>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Settings</p>
                    <p className="text-sm text-gray-500">Manage preferences</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center space-y-8">
            {/* Hero Section */}
            <div>
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-8">
                <span className="text-white text-4xl">🔐</span>
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Google Sign-In Demo
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                Production-ready authentication system with React and Django featuring 
                secure JWT cookies and Google Identity Services
              </p>
              
              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  href="/login" 
                  className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                >
                  Sign In to Your Account
                </Link>
                <Link 
                  href="/signup" 
                  className="inline-flex items-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                >
                  Create New Account
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Features Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-white text-2xl">🔐</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Secure Authentication</h3>
            <p className="text-gray-600">
              JWT tokens stored in HTTP-only cookies with automatic refresh for maximum security and seamless user experience.
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-white text-2xl">🌐</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Google Sign-In</h3>
            <p className="text-gray-600">
              One-click authentication with Google Identity Services and server-side credential verification for enhanced security.
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-white text-2xl">🎨</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Modern UI</h3>
            <p className="text-gray-600">
              Beautiful, responsive interface built with Tailwind CSS and modern React patterns for the best user experience.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
