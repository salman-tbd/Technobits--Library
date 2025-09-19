'use client'

import { useEffect, useState } from 'react'
import { CheckCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'

export interface NotificationProps {
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message: string
  duration?: number
  onClose?: () => void
}

export default function Notification({
  type,
  title,
  message,
  duration = 5000,
  onClose
}: NotificationProps) {
  const [isVisible, setIsVisible] = useState(true)
  const [isAnimating, setIsAnimating] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  // Start animation after mount to prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true)
    // Small delay to ensure smooth animation
    const animationTimer = setTimeout(() => {
      setIsAnimating(true)
    }, 50)

    return () => clearTimeout(animationTimer)
  }, [])

  useEffect(() => {
    // Auto-hide after duration, only after mounted
    if (duration > 0 && isMounted) {
      const timer = setTimeout(() => {
        handleClose()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, isMounted])

  const handleClose = () => {
    setIsAnimating(false)
    setTimeout(() => {
      setIsVisible(false)
      onClose?.()
    }, 300)
  }

  const getIconAndColors = () => {
    switch (type) {
      case 'success':
        return {
          icon: <CheckCircleIcon className="h-6 w-6" />,
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          iconColor: 'text-green-400',
          titleColor: 'text-green-800',
          messageColor: 'text-green-700'
        }
      case 'error':
        return {
          icon: <XCircleIcon className="h-6 w-6" />,
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          iconColor: 'text-red-400',
          titleColor: 'text-red-800',
          messageColor: 'text-red-700'
        }
      case 'warning':
        return {
          icon: <XCircleIcon className="h-6 w-6" />,
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          iconColor: 'text-yellow-400',
          titleColor: 'text-yellow-800',
          messageColor: 'text-yellow-700'
        }
      default: // info
        return {
          icon: <CheckCircleIcon className="h-6 w-6" />,
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          iconColor: 'text-blue-400',
          titleColor: 'text-blue-800',
          messageColor: 'text-blue-700'
        }
    }
  }

  // Don't render until mounted to prevent hydration mismatch
  if (!isVisible || !isMounted) return null

  const { icon, bgColor, borderColor, iconColor, titleColor, messageColor } = getIconAndColors()

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm w-full pointer-events-auto transition-all duration-300 transform ${
        isAnimating ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <div className={`${bgColor} ${borderColor} border rounded-lg shadow-lg overflow-hidden`}>
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <div className={iconColor}>
                {icon}
              </div>
            </div>
            <div className="ml-3 w-0 flex-1">
              <p className={`text-sm font-medium ${titleColor}`}>
                {title}
              </p>
              <p className={`mt-1 text-sm ${messageColor}`}>
                {message}
              </p>
            </div>
            <div className="ml-4 flex-shrink-0 flex">
              <button
                className={`${bgColor} rounded-md inline-flex ${titleColor} hover:${messageColor} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                onClick={handleClose}
              >
                <span className="sr-only">Close</span>
                <XMarkIcon className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
