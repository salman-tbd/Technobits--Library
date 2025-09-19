'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    // Check if error is from Chrome extension - don't show error UI for these
    const errorStack = error.stack || '';
    const isExtensionError = errorStack.includes('chrome-extension://') || 
                           errorStack.includes('extension') ||
                           error.message.includes('Minified React error #299');
    
    if (isExtensionError) {
      console.warn('Chrome extension error detected, not showing error UI:', error.message);
      return { hasError: false }; // Don't show error UI for extension errors
    }
    
    // Update state so the next render will show the fallback UI for real errors
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Check if error is from Chrome extension
    const errorStack = error.stack || '';
    const isExtensionError = errorStack.includes('chrome-extension://') || 
                           errorStack.includes('extension') ||
                           error.message.includes('Minified React error #299');
    
    if (isExtensionError) {
      console.warn('Chrome extension error caught and suppressed:', error.message);
      // Reset error state for extension errors
      setTimeout(() => {
        this.setState({ hasError: false, error: undefined });
      }, 100);
      return;
    }
    
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Something went wrong</h2>
            <p className="text-gray-600 mb-4">
              There was an error loading the application. Please try refreshing the page.
            </p>
            <button 
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
