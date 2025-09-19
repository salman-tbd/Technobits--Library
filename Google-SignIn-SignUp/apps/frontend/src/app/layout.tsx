import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthProvider } from "../contexts/AuthContext";
import { RecaptchaProvider } from "../contexts/RecaptchaContext";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Google Sign-In/Sign-Up - Authentication Demo",
  description: "Production-ready authentication system with React and Django",
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
            {children}
          </AuthProvider>
        </RecaptchaProvider>
      </body>
    </html>
  );
}
