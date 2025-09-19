'use client'

import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import Notification, { NotificationProps } from '../components/Notification'

interface NotificationContextType {
  showNotification: (notification: Omit<NotificationProps, 'onClose'>) => void
  removeNotification: (id: string) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

interface NotificationWithId extends NotificationProps {
  id: string
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<NotificationWithId[]>([])
  const [isMounted, setIsMounted] = useState(false)

  // Prevent hydration mismatches by only rendering notifications after mount
  // Add extra delay on first load to avoid extension interference
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMounted(true)
    }, 100) // Small delay to let extensions settle
    
    return () => clearTimeout(timer)
  }, [])

  const showNotification = (notification: Omit<NotificationProps, 'onClose'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newNotification: NotificationWithId = {
      ...notification,
      id,
      onClose: () => removeNotification(id)
    }
    
    setNotifications(prev => [...prev, newNotification])
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  return (
    <NotificationContext.Provider value={{ showNotification, removeNotification }}>
      {children}
      {/* Only render notifications after hydration to prevent SSR mismatch */}
      {isMounted && (
        <div className="fixed top-0 right-0 p-4 z-50 space-y-4">
          {notifications.map((notification) => (
            <Notification
              key={notification.id}
              type={notification.type}
              title={notification.title}
              message={notification.message}
              duration={notification.duration}
              onClose={notification.onClose}
            />
          ))}
        </div>
      )}
    </NotificationContext.Provider>
  )
}

export function useNotification() {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider')
  }
  return context
}
