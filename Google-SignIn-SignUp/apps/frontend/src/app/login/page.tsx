"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LoginForm } from "../../components/LoginForm";
import { SimpleGoogleButton } from "../../components/SimpleGoogleButton";

export default function LoginPage() {
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const router = useRouter();

  const handleLoginSuccess = () => {
    setError("");
    setSuccess("Login successful! Redirecting...");
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
          onSuccess={handleLoginSuccess}
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
