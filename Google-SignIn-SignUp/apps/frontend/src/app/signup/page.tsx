"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SignupForm } from "../../components/SignupForm";
import { SimpleGoogleButton } from "../../components/SimpleGoogleButton";

export default function SignupPage() {
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const router = useRouter();

  const handleSignupSuccess = () => {
    setError("");
    setSuccess("Account created successfully! Redirecting...");
    setTimeout(() => {
      router.push("/");
    }, 1000);
  };

  const handleSignupError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess("");
  };

  const handleGoogleSuccess = () => {
    setError("");
    setSuccess("Google sign-up successful! Redirecting...");
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
        <h1 className="page-title">Join Us Today! 🚀</h1>
        <p className="page-subtitle">
          Create your account and start your authentication journey
        </p>
      </div>

      <div className="max-w-md mx-auto">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <SignupForm
          onSuccess={handleSignupSuccess}
          onError={handleSignupError}
        />

        <div className="divider">
          <span>or continue with</span>
        </div>

        <SimpleGoogleButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text="signup_with"
        />

        <div className="text-center mt-8">
          <p className="text-gray-600 mb-4">
            Already have an account?
          </p>
          <Link href="/login" className="btn-primary">
            Sign In Instead
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
