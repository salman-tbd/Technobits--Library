"use client";

import React from "react";
import { QRCodeDisplayProps } from "../lib/types";

export const TwoFactorQRCode: React.FC<QRCodeDisplayProps> = ({
  qrCodeImage,
  secretKey,
  onContinue,
  className = "",
}) => {
  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(secretKey);
      // You could add a toast notification here
    } catch (err) {
      console.error("Failed to copy secret:", err);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl">📱</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Set Up Two-Factor Authentication
        </h2>
        <p className="text-gray-600">
          Scan the QR code with your authenticator app to get started
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
          <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            1
          </span>
          Install an Authenticator App
        </h3>
        <p className="text-blue-800 text-sm mb-3">
          Download one of these apps on your mobile device:
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Google Authenticator
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Authy
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Microsoft Authenticator
          </span>
        </div>
      </div>

      {/* QR Code Section */}
      <div className="bg-white rounded-xl shadow-lg border p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
          <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            2
          </span>
          Scan QR Code
        </h3>
        
        <div className="flex flex-col items-center space-y-4">
          {/* QR Code Image */}
          <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
            <img
              src={qrCodeImage}
              alt="Two-Factor Authentication QR Code"
              className="w-48 h-48 object-contain"
            />
          </div>
          
          <p className="text-sm text-gray-600 text-center max-w-sm">
            Open your authenticator app and scan this QR code to add your account
          </p>
        </div>
      </div>

      {/* Manual Entry Option */}
      <div className="bg-gray-50 rounded-lg p-4 border">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 bg-gray-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            ⚙️
          </span>
          Can't scan? Enter manually
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          If you can't scan the QR code, you can manually enter this secret key:
        </p>
        
        <div className="flex items-center space-x-2">
          <div className="flex-1 bg-white border rounded-md px-3 py-2">
            <code className="text-sm font-mono text-gray-800 break-all">
              {secretKey}
            </code>
          </div>
          <button
            onClick={copySecret}
            className="px-3 py-2 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
          >
            Copy
          </button>
        </div>
      </div>

      {/* Next Step */}
      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
        <h3 className="font-semibold text-green-900 mb-2 flex items-center">
          <span className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            3
          </span>
          Next Step
        </h3>
        <p className="text-green-800 text-sm">
          After adding the account to your authenticator app, you'll need to enter a 6-digit code to verify the setup.
        </p>
      </div>

      {/* Continue Button */}
      {onContinue && (
        <div className="flex justify-center pt-4">
          <button
            onClick={onContinue}
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            I've Added This Account
          </button>
        </div>
      )}

      {/* Security Notice */}
      <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
        <div className="flex items-start">
          <span className="text-yellow-600 mr-2">⚠️</span>
          <div>
            <h4 className="font-medium text-yellow-900 text-sm">Security Notice</h4>
            <p className="text-yellow-800 text-xs mt-1">
              Keep your secret key and backup codes in a secure location. Anyone with access to these can access your account.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
