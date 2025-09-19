"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../../contexts/AuthContext";
import { LoginForm } from "../../components/LoginForm";
import { SimpleGoogleButton } from "../../components/SimpleGoogleButton";
import { TwoFactorLoginVerify } from "../../components/TwoFactorLoginVerify";
import { User, TwoFactorLoginResponse } from "../../lib/types";

type LoginStep = 'credentials' | '2fa-verify';

export default function LoginPage() {
  const { completeTwoFactorLogin } = useAuth();
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [currentStep, setCurrentStep] = useState<LoginStep>('credentials');
  const [twoFactorData, setTwoFactorData] = useState<{
    tempToken: string;
    userId: number;
    backupCodesAvailable: boolean;
  } | null>(null);
  const router = useRouter();

  const handleLoginResponse = (response: TwoFactorLoginResponse) => {
    setError("");
    
    if (response.requires_2fa) {
      // 2FA is required
      if (response.temp_token && response.user_id) {
        setTwoFactorData({
          tempToken: response.temp_token,
          userId: response.user_id,
          backupCodesAvailable: response.backup_codes_available || false,
        });
        setCurrentStep('2fa-verify');
        setSuccess("Please complete two-factor authentication.");
      } else {
        setError("Invalid 2FA response from server. Please try again.");
      }
    } else if (response.user) {
      // No 2FA required, user is logged in
      handleDirectLoginSuccess();
    } else {
      setError("Invalid login response from server.");
    }
  };

  const handleDirectLoginSuccess = () => {
    setError("");
    setSuccess("Login successful! Redirecting...");
    setTimeout(() => {
      router.push("/");
    }, 1000);
  };

  const handleTwoFactorSuccess = (user: User) => {
    completeTwoFactorLogin(user);
    setError("");
    setSuccess("Two-factor authentication completed! Redirecting...");
    setTimeout(() => {
      router.push("/");
    }, 1000);
  };

  const handleLoginError = (errorMessage: string) => {
    if (errorMessage) {
      setError(errorMessage);
    } else {
      setError("");
    }
    setSuccess("");
  };

  const handleForgotPasswordSuccess = (message: string) => {
    setError("");
    if (message) {
      setSuccess(message);
    } else {
      setSuccess("");
    }
  };

  const handleGoogleSuccess = () => {
    setError("");
    setSuccess("Google sign-in successful! Redirecting...");
    setTimeout(() => {
      router.push("/");
    }, 1000);
  };

  const handleGoogleError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess("");
  };

  const goBackToCredentials = () => {
    setCurrentStep('credentials');
    setTwoFactorData(null);
    setError("");
    setSuccess("");
  };

  // Show 2FA verification if required
  if (currentStep === '2fa-verify' && twoFactorData) {
    return (
      <div className="page-container">
        <div className="max-w-md mx-auto">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <TwoFactorLoginVerify
            tempToken={twoFactorData.tempToken}
            userId={twoFactorData.userId}
            backupCodesAvailable={twoFactorData.backupCodesAvailable}
            onSuccess={handleTwoFactorSuccess}
            onError={handleLoginError}
          />

          <div className="text-center mt-6">
            <button
              onClick={goBackToCredentials}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium focus:outline-none focus:underline"
            >
              ← Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Standard login form
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Welcome Back! 👋</h1>
        <p className="page-subtitle">
          Sign in to your account to continue your journey
        </p>
      </div>

      <div className="max-w-md mx-auto">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <LoginForm
          onLoginResponse={handleLoginResponse}
          onError={handleLoginError}
          onForgotPasswordSuccess={handleForgotPasswordSuccess}
        />

        <div className="divider">
          <span>or continue with</span>
        </div>

        <SimpleGoogleButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text="signin_with"
        />

        <div className="text-center mt-8">
          <p className="text-gray-600 mb-4">
            Don&apos;t have an account yet?
          </p>
          <Link href="/signup" className="btn-secondary">
            Create New Account
          </Link>
        </div>

        <div className="text-center mt-6">
          <Link href="/" className="btn-outline">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
