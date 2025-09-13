import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthProvider } from "../contexts/AuthContext";
import { RecaptchaProvider } from "../contexts/RecaptchaContext";
import { NotificationProvider } from "../contexts/NotificationContext";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Technobits Directory - Modern Web Integration Showcase",
  description: "Complete authentication and payment integration examples with Google Auth, Google Pay, and PayPal - built with Next.js 14 and Django 5.0",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8007";
  const recaptchaSiteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || "";
  
  // Debug: Log environment variables on server restart
  if (typeof window !== 'undefined') {
    console.log("🔍 Environment Debug:");
    console.log("API Base URL:", process.env.NEXT_PUBLIC_API_BASE_URL);
    console.log("Google Client ID:", process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID);
    console.log("Full Client ID Length:", process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.length);
    console.log("reCAPTCHA Site Key:", recaptchaSiteKey ? "✓ Configured" : "❌ Missing");
  }
  

  return (
    <html lang="en">
      <body className={inter.className}>
        <RecaptchaProvider siteKey={recaptchaSiteKey}>
          <AuthProvider apiBaseUrl={apiBaseUrl}>
            <NotificationProvider>
              {children}
            </NotificationProvider>
          </AuthProvider>
        </RecaptchaProvider>
      </body>
    </html>
  );
}
