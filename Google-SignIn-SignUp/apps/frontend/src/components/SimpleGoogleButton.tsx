"use client";

import React, { useEffect, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";

interface SimpleGoogleButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  text?: string;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: any) => void }) => void;
          renderButton: (element: HTMLElement, options: any) => void;
        };
      };
    };
  }
}

export const SimpleGoogleButton: React.FC<SimpleGoogleButtonProps> = ({
  onSuccess,
  onError,
  text = "signin_with",
}) => {
  const buttonRef = useRef<HTMLDivElement>(null);
  const { googleLoginWithCredential } = useAuth();
  const initializationAttempted = useRef(false);

  useEffect(() => {
    // Prevent multiple initializations
    if (initializationAttempted.current) return;
    initializationAttempted.current = true;

    const CLIENT_ID = "197422923252-vpk2s8bf2s20hv18f87mus1jm399vrfn.apps.googleusercontent.com";
    console.log("🚀 SimpleGoogleButton: Starting with Client ID:", CLIENT_ID);

    const handleGoogleResponse = async (response: { credential: string }) => {
      console.log("📨 Google response received");
      try {
        await googleLoginWithCredential(response.credential);
        onSuccess?.();
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Google sign-in failed";
        console.error("❌ Google login error:", errorMessage);
        onError?.(errorMessage);
      }
    };

    const initializeGoogleButton = () => {
      // Check if Google SDK is loaded
      if (!window.google?.accounts?.id) {
        console.log("⏳ Google SDK not ready, retrying...");
        setTimeout(initializeGoogleButton, 100);
        return;
      }

      // Check if button element is ready
      if (!buttonRef.current) {
        console.log("⏳ Button element not ready, retrying...");
        setTimeout(initializeGoogleButton, 100);
        return;
      }

      console.log("✅ Both Google SDK and button element are ready");

      try {
        // Initialize Google Sign-In
        window.google.accounts.id.initialize({
          client_id: CLIENT_ID,
          callback: handleGoogleResponse,
        });

        console.log("✅ Google initialized, rendering button...");

        // Render the button
        window.google.accounts.id.renderButton(buttonRef.current, {
          theme: "outline",
          size: "large",
          type: "standard",
          text: text,
          width: "100%",
        });

        console.log("✅ Google button rendered successfully!");
      } catch (error) {
        console.error("❌ Failed to initialize/render Google button:", error);
      }
    };

    // Load Google SDK if not already loaded
    const existingScript = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
    
    if (existingScript) {
      console.log("📜 Google SDK script already exists");
      initializeGoogleButton();
    } else {
      console.log("📜 Loading Google SDK script...");
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = () => {
        console.log("✅ Google SDK script loaded");
        initializeGoogleButton();
      };
      script.onerror = () => {
        console.error("❌ Failed to load Google SDK script");
      };
      document.head.appendChild(script);
    }
  }, [googleLoginWithCredential, onSuccess, onError, text]);

  return (
    <div className="w-full">
      <div ref={buttonRef} className="w-full min-h-[44px] flex items-center justify-center">
        {/* Fallback content while loading */}
        <div className="flex items-center justify-center gap-3 w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-600">
          <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
          <span className="text-sm font-medium">Loading Google Sign-In...</span>
        </div>
      </div>
    </div>
  );
};
