'use client'

import { useEffect } from 'react'

export default function ClientExtensionHandler() {
  useEffect(() => {
    // Add additional error suppression after React hydration
    const handleExtensionError = (event: ErrorEvent) => {
      if (event.filename && event.filename.includes('chrome-extension://')) {
        console.warn('Post-hydration extension error suppressed:', event.message);
        event.stopImmediatePropagation();
        event.preventDefault();
        return false;
      }
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (event.reason && event.reason.stack && event.reason.stack.includes('chrome-extension://')) {
        console.warn('Post-hydration extension promise rejection suppressed:', event.reason);
        event.preventDefault();
        return false;
      }
    };

    // Add listeners with high priority
    window.addEventListener('error', handleExtensionError, { capture: true });
    window.addEventListener('unhandledrejection', handleUnhandledRejection, { capture: true });

    return () => {
      window.removeEventListener('error', handleExtensionError, { capture: true });
      window.removeEventListener('unhandledrejection', handleUnhandledRejection, { capture: true });
    };
  }, []);

  return null; // This component doesn't render anything
}
