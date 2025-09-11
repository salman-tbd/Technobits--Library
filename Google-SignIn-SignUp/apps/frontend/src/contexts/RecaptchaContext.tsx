"use client";

import React, { createContext, useContext, useCallback, ReactNode } from 'react';
import { GoogleReCaptchaProvider, useGoogleReCaptcha } from 'react-google-recaptcha-v3';

interface RecaptchaContextType {
  executeRecaptcha: (action: string) => Promise<string | null>;
  isRecaptchaLoaded: boolean;
}

const RecaptchaContext = createContext<RecaptchaContextType | undefined>(undefined);

interface RecaptchaProviderProps {
  children: ReactNode;
  siteKey: string;
}

// Inner component that uses the Google reCAPTCHA hook
const RecaptchaContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { executeRecaptcha: googleExecuteRecaptcha } = useGoogleReCaptcha();

  const executeRecaptcha = useCallback(
    async (action: string): Promise<string | null> => {
      if (!googleExecuteRecaptcha) {
        console.warn('reCAPTCHA not loaded yet');
        return null;
      }

      try {
        const token = await googleExecuteRecaptcha(action);
        return token;
      } catch (error) {
        console.error('Error executing reCAPTCHA:', error);
        return null;
      }
    },
    [googleExecuteRecaptcha]
  );

  const isRecaptchaLoaded = !!googleExecuteRecaptcha;

  return (
    <RecaptchaContext.Provider value={{ executeRecaptcha, isRecaptchaLoaded }}>
      {children}
    </RecaptchaContext.Provider>
  );
};

// Main provider that wraps Google's provider
export const RecaptchaProvider: React.FC<RecaptchaProviderProps> = ({ 
  children, 
  siteKey 
}) => {
  if (!siteKey) {
    console.warn('reCAPTCHA site key not provided');
    // Return children without reCAPTCHA if no site key
    return <>{children}</>;
  }

  return (
    <GoogleReCaptchaProvider
      reCaptchaKey={siteKey}
      scriptProps={{
        async: false,
        defer: false,
        appendTo: "head",
        nonce: undefined,
      }}
    >
      <RecaptchaContextProvider>{children}</RecaptchaContextProvider>
    </GoogleReCaptchaProvider>
  );
};

// Hook to use reCAPTCHA
export const useRecaptcha = (): RecaptchaContextType => {
  const context = useContext(RecaptchaContext);
  if (context === undefined) {
    throw new Error('useRecaptcha must be used within a RecaptchaProvider');
  }
  return context;
};

// Hook for form submissions with reCAPTCHA
export const useRecaptchaForm = () => {
  const { executeRecaptcha, isRecaptchaLoaded } = useRecaptcha();

  const getRecaptchaToken = useCallback(
    async (action: string): Promise<string | null> => {
      if (!isRecaptchaLoaded) {
        console.warn('reCAPTCHA not loaded, proceeding without token');
        return null;
      }

      const token = await executeRecaptcha(action);
      if (!token) {
        console.warn('Failed to get reCAPTCHA token');
      }
      
      return token;
    },
    [executeRecaptcha, isRecaptchaLoaded]
  );

  return {
    getRecaptchaToken,
    isRecaptchaLoaded,
  };
};
