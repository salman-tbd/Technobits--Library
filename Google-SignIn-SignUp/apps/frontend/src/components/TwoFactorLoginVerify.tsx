"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { TwoFactorLoginVerifyProps, TwoFactorRateLimitError } from "../lib/types";
import { useAuth } from "../contexts/AuthContext";

// Validation schemas
const totpSchema = z.object({
  totpCode: z
    .string()
    .min(6, "Code must be 6 digits")
    .max(6, "Code must be 6 digits")
    .regex(/^\d{6}$/, "Code must be 6 digits"),
});

const backupSchema = z.object({
  backupCode: z
    .string()
    .min(8, "Backup code must be 8 characters")
    .max(8, "Backup code must be 8 characters")
    .regex(/^[A-Z0-9]{8}$/, "Invalid backup code format"),
});

type TotpFormData = z.infer<typeof totpSchema>;
type BackupFormData = z.infer<typeof backupSchema>;

export const TwoFactorLoginVerify: React.FC<TwoFactorLoginVerifyProps> = ({
  tempToken,
  userId,
  backupCodesAvailable,
  onSuccess,
  onError,
  className = "",
}) => {
  const { apiClient } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [rateLimitInfo, setRateLimitInfo] = useState<TwoFactorRateLimitError | null>(null);

  const totpForm = useForm<TotpFormData>({
    resolver: zodResolver(totpSchema),
    mode: "onChange",
  });

  const backupForm = useForm<BackupFormData>({
    resolver: zodResolver(backupSchema),
    mode: "onChange",
  });

  const currentForm = useBackupCode ? backupForm : totpForm;

  const handleSubmit = async (data: TotpFormData | BackupFormData) => {
    setIsSubmitting(true);
    setRateLimitInfo(null);
    
    try {
      const response = await apiClient.twoFactorLoginComplete(
        tempToken,
        userId,
        useBackupCode ? undefined : (data as TotpFormData).totpCode,
        useBackupCode ? (data as BackupFormData).backupCode : undefined
      );
      
      onSuccess?.(response.user);
    } catch (error: any) {
      // Handle rate limiting specifically
      if (error.details?.rate_limited) {
        setRateLimitInfo(error.details as TwoFactorRateLimitError);
      }
      
      onError?.(error.message || "Verification failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const switchMode = () => {
    setUseBackupCode(!useBackupCode);
    totpForm.reset();
    backupForm.reset();
    setRateLimitInfo(null);
  };

  const isRateLimited = rateLimitInfo?.rate_limited || false;
  const remainingAttempts = rateLimitInfo?.remaining_attempts ?? null;

  return (
    <div className={`max-w-md mx-auto space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl">🔐</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Two-Factor Authentication Required
        </h2>
        <p className="text-gray-600">
          {useBackupCode 
            ? "Enter one of your backup codes to continue" 
            : "Enter the 6-digit code from your authenticator app"
          }
        </p>
      </div>

      {/* Rate limiting warning */}
      {isRateLimited && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <span className="text-red-600 mr-2">🚨</span>
            <div>
              <h4 className="font-medium text-red-900">Account Temporarily Locked</h4>
              <p className="text-sm text-red-800 mt-1">
                {rateLimitInfo?.rate_limit_message || "Too many failed attempts. Please try again later."}
              </p>
              {rateLimitInfo?.lockout_ends_at && (
                <p className="text-xs text-red-700 mt-2">
                  Lockout ends: {new Date(rateLimitInfo.lockout_ends_at).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Remaining attempts warning */}
      {!isRateLimited && remainingAttempts !== null && remainingAttempts < 3 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <div className="flex items-center">
            <span className="text-orange-600 mr-2">⚠️</span>
            <p className="text-sm text-orange-800">
              {remainingAttempts > 0 
                ? `${remainingAttempts} attempt${remainingAttempts !== 1 ? 's' : ''} remaining before temporary lockout`
                : "Final attempt before lockout"
              }
            </p>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={currentForm.handleSubmit(handleSubmit)} className="space-y-6">
        {!useBackupCode ? (
          /* TOTP Code Input */
          <div>
            <label htmlFor="totpCode" className="block text-sm font-medium text-gray-700 mb-2">
              Authentication Code
            </label>
            <input
              id="totpCode"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="000000"
              maxLength={6}
              {...totpForm.register("totpCode")}
              className={`w-full px-4 py-3 text-center text-2xl font-mono tracking-widest border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                totpForm.formState.errors.totpCode 
                  ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                  : 'border-gray-300'
              }`}
              disabled={isSubmitting || isRateLimited}
              autoFocus
            />
            {totpForm.formState.errors.totpCode && (
              <p className="mt-2 text-sm text-red-600">
                {totpForm.formState.errors.totpCode.message}
              </p>
            )}
            
            {/* Time-based code notice */}
            <div className="mt-3 flex items-center justify-center text-sm text-gray-500">
              <span className="w-4 h-4 mr-2">⏰</span>
              <span>Codes refresh every 30 seconds</span>
            </div>
          </div>
        ) : (
          /* Backup Code Input */
          <div>
            <label htmlFor="backupCode" className="block text-sm font-medium text-gray-700 mb-2">
              Backup Code
            </label>
            <input
              id="backupCode"
              type="text"
              placeholder="ABC12345"
              maxLength={8}
              {...backupForm.register("backupCode")}
              className={`w-full px-4 py-3 text-center text-xl font-mono tracking-widest uppercase border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                backupForm.formState.errors.backupCode 
                  ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                  : 'border-gray-300'
              }`}
              disabled={isSubmitting || isRateLimited}
              autoFocus
              onChange={(e) => {
                e.target.value = e.target.value.toUpperCase();
                backupForm.setValue("backupCode", e.target.value);
              }}
            />
            {backupForm.formState.errors.backupCode && (
              <p className="mt-2 text-sm text-red-600">
                {backupForm.formState.errors.backupCode.message}
              </p>
            )}
            
            {/* Backup code notice */}
            <div className="mt-3 bg-yellow-50 rounded-lg p-3 border border-yellow-200">
              <div className="flex items-start">
                <span className="text-yellow-600 mr-2">⚠️</span>
                <p className="text-sm text-yellow-800">
                  Each backup code can only be used once. Make sure to save your remaining codes.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || !currentForm.formState.isValid || isRateLimited}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? (
            <div className="flex items-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Verifying...
            </div>
          ) : isRateLimited ? (
            "Account Locked"
          ) : (
            "Complete Sign In"
          )}
        </button>

        {/* Switch between TOTP and backup code */}
        {backupCodesAvailable && !isRateLimited && (
          <div className="text-center">
            <button
              type="button"
              onClick={switchMode}
              className="text-sm text-blue-600 hover:text-blue-700 focus:outline-none focus:underline"
              disabled={isSubmitting}
            >
              {useBackupCode 
                ? "Use authenticator app instead"
                : "Lost your device? Use a backup code"
              }
            </button>
          </div>
        )}
      </form>

      {/* Security Notice */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-start">
          <span className="text-blue-600 mr-2">🛡️</span>
          <div>
            <h4 className="font-medium text-blue-900 text-sm">Secure Login</h4>
            <p className="text-xs text-blue-800 mt-1">
              This extra step helps protect your account from unauthorized access.
            </p>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-gray-50 rounded-lg p-4 border">
        <h4 className="font-medium text-gray-900 mb-2 flex items-center text-sm">
          <span className="w-4 h-4 mr-2">💡</span>
          Need Help?
        </h4>
        <div className="text-xs text-gray-600 space-y-1">
          <p>• Make sure your device's time is correct</p>
          <p>• Try refreshing your authenticator app</p>
          {backupCodesAvailable && <p>• Use a backup code if your device is unavailable</p>}
          <p>• Contact support if you've lost access to all authentication methods</p>
        </div>
      </div>
    </div>
  );
};
