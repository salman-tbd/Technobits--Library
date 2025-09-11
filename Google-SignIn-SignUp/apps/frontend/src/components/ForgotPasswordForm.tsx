"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { forgotPasswordSchema, ForgotPasswordFormData } from "../lib/validation";
import { useAuth } from "../contexts/AuthContext";
import { useRecaptchaForm } from "../contexts/RecaptchaContext";

interface ForgotPasswordFormProps {
  onSuccess?: (message: string) => void;
  onError?: (error: string) => void;
  onBackToLogin?: () => void;
  className?: string;
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
  onSuccess,
  onError,
  onBackToLogin,
  className = "",
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { getRecaptchaToken, isRecaptchaLoaded } = useRecaptchaForm();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    mode: "onChange",
  });

  const { apiClient } = useAuth();

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsSubmitting(true);

    try {
      // Get reCAPTCHA token before submitting
      const recaptchaToken = await getRecaptchaToken('forgot_password');
      
      const response = await apiClient.forgotPassword(data.email, recaptchaToken || undefined);
      onSuccess?.(response.message);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send reset instructions";
      onError?.(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={`space-y-6 ${className}`}>

      {/* Instructions */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Forgot Password?</h2>
        <p className="text-sm text-gray-600">
          Enter your email address and we&apos;ll send you instructions to reset your password.
        </p>
      </div>

      {/* Email Address */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          {...register("email")}
          className={`w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.email 
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
              : 'border-gray-300'
          }`}
          placeholder="Enter your email address"
          disabled={isSubmitting}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      {/* reCAPTCHA Notice */}
      {!isRecaptchaLoaded && (
        <div className="text-xs text-gray-500 text-center">
          Loading security verification...
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting || !isValid}
        className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? (
          <div className="flex items-center">
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            Sending Instructions...
          </div>
        ) : (
          "Send Reset Instructions"
        )}
      </button>
      
      {/* reCAPTCHA Disclaimer */}
      <div className="text-xs text-gray-500 text-center">
        This site is protected by reCAPTCHA and the Google{' '}
        <a href="https://policies.google.com/privacy" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
          Privacy Policy
        </a>{' '}
        and{' '}
        <a href="https://policies.google.com/terms" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
          Terms of Service
        </a>{' '}
        apply.
      </div>

      {/* Back to Login */}
      <div className="text-center">
        <button
          type="button"
          onClick={onBackToLogin}
          className="text-sm text-blue-600 hover:text-blue-500 font-medium"
        >
          ← Back to Sign In
        </button>
      </div>
    </form>
  );
};
