"use client";

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import { TwoFactorSettings } from '../../components/TwoFactorSettings';

type DashboardSection = 'overview' | 'security' | 'profile';

export default function DashboardPage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const section = (searchParams.get('section') as DashboardSection) || 'overview';
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const navigateToSection = (newSection: DashboardSection) => {
    router.push(`/dashboard?section=${newSection}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white shadow-lg rounded-xl p-6">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-white text-2xl">👋</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.name || user.email.split('@')[0]}!
            </h2>
            <p className="text-gray-600">Manage your account and security settings</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow-lg rounded-xl p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-green-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Account Status</h3>
              <p className="text-lg font-semibold text-gray-900">Active & Verified</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-xl p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 text-xl">🔐</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Security</h3>
              <p className="text-lg font-semibold text-gray-900">Protected</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-xl p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-purple-600 text-xl">📧</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Email</h3>
              <p className="text-lg font-semibold text-gray-900">Verified</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow-lg rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            onClick={() => navigateToSection('security')}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-blue-600">🔐</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Security Settings</p>
              <p className="text-sm text-gray-500">Manage 2FA and passwords</p>
            </div>
          </button>

          <button
            onClick={() => navigateToSection('profile')}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-green-600">👤</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Profile Settings</p>
              <p className="text-sm text-gray-500">Update your information</p>
            </div>
          </button>

          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left disabled:opacity-50"
          >
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-red-600">🚪</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">
                {isLoggingOut ? 'Signing Out...' : 'Sign Out'}
              </p>
              <p className="text-sm text-gray-500">End your session</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  const renderProfile = () => (
    <div className="space-y-6">
      <div className="bg-white shadow-lg rounded-xl p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Information</h2>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center py-3 border-b border-gray-100">
            <span className="text-gray-600 font-medium">Email Address</span>
            <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded">
              {user.email}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-3 border-b border-gray-100">
            <span className="text-gray-600 font-medium">Display Name</span>
            <span className="text-gray-900">
              {user.name || 'Not set'}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-3 border-b border-gray-100">
            <span className="text-gray-600 font-medium">User ID</span>
            <span className="text-gray-900 font-mono text-sm bg-gray-50 px-3 py-1 rounded">
              {user.id}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-3">
            <span className="text-gray-600 font-medium">Account Status</span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Active
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (section) {
      case 'security':
        return <TwoFactorSettings />;
      case 'profile':
        return renderProfile();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🔐</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Account Dashboard</h1>
                <p className="text-sm text-gray-500">Secure Authentication System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user.name || user.email.split('@')[0]}
                </p>
                <p className="text-xs text-gray-500">{user.email}</p>
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
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <div className="lg:w-64">
            <nav className="bg-white shadow-lg rounded-xl p-4">
              <ul className="space-y-2">
                <li>
                  <button
                    onClick={() => navigateToSection('overview')}
                    className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors flex items-center space-x-3 ${
                      section === 'overview'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-lg">📊</span>
                    <span>Overview</span>
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => navigateToSection('security')}
                    className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors flex items-center space-x-3 ${
                      section === 'security'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-lg">🔐</span>
                    <span>Security Settings</span>
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => navigateToSection('profile')}
                    className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors flex items-center space-x-3 ${
                      section === 'profile'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-lg">👤</span>
                    <span>Profile</span>
                  </button>
                </li>
              </ul>
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => router.push('/')}
                  className="w-full text-left px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors flex items-center space-x-3"
                >
                  <span className="text-lg">🏠</span>
                  <span>Back to Home</span>
                </button>
              </div>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
}
