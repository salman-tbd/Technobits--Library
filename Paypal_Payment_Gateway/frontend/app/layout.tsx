import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { NotificationProvider } from '../contexts/NotificationContext'
import ErrorBoundary from '../components/ErrorBoundary'
import ClientExtensionHandler from '../components/ClientExtensionHandler'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'E-commerce PayPal Integration',
  description: 'Demo e-commerce site with PayPal checkout integration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Suppress Chrome extension errors that interfere with React hydration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Suppress extension errors during initial load
              window.addEventListener('error', function(e) {
                if (e.filename && e.filename.includes('chrome-extension://')) {
                  console.warn('Chrome extension error suppressed during hydration:', e.message);
                  e.stopPropagation();
                  e.preventDefault();
                  return false;
                }
              });
              
              // Suppress unhandled promise rejections from extensions
              window.addEventListener('unhandledrejection', function(e) {
                if (e.reason && e.reason.stack && e.reason.stack.includes('chrome-extension://')) {
                  console.warn('Chrome extension promise rejection suppressed:', e.reason);
                  e.preventDefault();
                  return false;
                }
              });
            `
          }}
        />
      </head>
      <body className={inter.className}>
        <ClientExtensionHandler />
        <ErrorBoundary>
          <NotificationProvider>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
              <main>{children}</main>
            </div>
          </NotificationProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
