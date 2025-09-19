"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { TwoFactorSettingsProps, TwoFactorStatus } from "../lib/types";
import { TwoFactorQRCode } from "./TwoFactorQRCode";
import { TwoFactorVerifyForm } from "./TwoFactorVerifyForm";
import { BackupCodesDisplay } from "./BackupCodesDisplay";

type SetupStep = 'status' | 'setup' | 'verify' | 'backup-codes';
type DisableStep = 'verify-disable' | 'confirming';

export const TwoFactorSettings: React.FC<TwoFactorSettingsProps> = ({
  onStatusChange,
  className = "",
}) => {
  const { apiClient } = useAuth();
  const [status, setStatus] = useState<TwoFactorStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [currentStep, setCurrentStep] = useState<SetupStep>('status');
  const [disableStep, setDisableStep] = useState<DisableStep>('verify-disable');
  
  // Setup flow state
  const [setupData, setSetupData] = useState<{
    secretKey: string;
    qrCodeImage: string;
    qrCodeUri: string;
  } | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  
  // Disable flow state
  const [disablePassword, setDisablePassword] = useState("");
  const [showDisableForm, setShowDisableForm] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const statusData = await apiClient.twoFactorStatus();
      setStatus(statusData);
    } catch (error: any) {
      setError(error.message || "Failed to load 2FA status");
    } finally {
      setLoading(false);
    }
  };

  const startSetup = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await apiClient.twoFactorSetup();
      setSetupData({
        secretKey: response.secret_key,
        qrCodeImage: response.qr_code_image,
        qrCodeUri: response.qr_code_uri,
      });
      setCurrentStep('setup');
    } catch (error: any) {
      setError(error.message || "Failed to start 2FA setup");
    } finally {
      setLoading(false);
    }
  };

  const proceedToVerification = () => {
    setCurrentStep('verify');
  };

  const handleSetupVerification = async (method: 'totp' | 'backup') => {
    // This will be called from the verification form
    // We need to implement the enable API call here
  };

  const handleEnable = async (totpCode: string) => {
    try {
      setLoading(true);
      setError("");
      const response = await apiClient.twoFactorEnable(totpCode);
      setBackupCodes(response.backup_codes);
      setCurrentStep('backup-codes');
      onStatusChange?.(true);
    } catch (error: any) {
      setError(error.message || "Failed to enable 2FA");
      setLoading(false);
    }
  };

  const finishSetup = () => {
    setCurrentStep('status');
    setSetupData(null);
    setBackupCodes([]);
    setLoading(false);
    loadStatus();
  };

  const startDisable = () => {
    setShowDisableForm(true);
    setDisableStep('verify-disable');
    setError("");
  };

  const handleDisable = async (password: string, totpCode?: string, backupCode?: string) => {
    try {
      setLoading(true);
      setError("");
      await apiClient.twoFactorDisable(password, totpCode, backupCode);
      setShowDisableForm(false);
      setDisablePassword("");
      onStatusChange?.(false);
      loadStatus();
    } catch (error: any) {
      setError(error.message || "Failed to disable 2FA");
    } finally {
      setLoading(false);
    }
  };

  const cancelAction = () => {
    setCurrentStep('status');
    setShowDisableForm(false);
    setSetupData(null);
    setBackupCodes([]);
    setDisablePassword("");
    setError("");
  };

  if (loading && currentStep === 'status') {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="text-center py-8">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading 2FA settings...</p>
        </div>
      </div>
    );
  }

  // Setup flow screens
  if (currentStep === 'setup' && setupData) {
    return (
      <TwoFactorQRCode
        qrCodeImage={setupData.qrCodeImage}
        secretKey={setupData.secretKey}
        onContinue={proceedToVerification}
        className={className}
      />
    );
  }

  if (currentStep === 'verify' && setupData) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Verify Your Setup
          </h2>
          <p className="text-gray-600">
            Enter a code from your authenticator app to complete setup
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-lg border p-6">
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              6-digit code from your authenticator app
            </label>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="000000"
              className="w-full px-4 py-3 text-center text-2xl font-mono tracking-widest border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onChange={(e) => {
                if (e.target.value.length === 6) {
                  handleEnable(e.target.value);
                }
              }}
              disabled={loading}
            />
          </div>
          
          <div className="flex gap-3 mt-6">
            <button
              onClick={cancelAction}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'backup-codes' && backupCodes.length > 0) {
    return (
      <BackupCodesDisplay
        codes={backupCodes}
        onClose={finishSetup}
        className={className}
      />
    );
  }

  // Main settings interface
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl">🔐</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Two-Factor Authentication
        </h2>
        <p className="text-gray-600">
          Enhance your account security with an additional layer of protection
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Current Status */}
      <div className="bg-white rounded-xl shadow-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Current Status</h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            status?.is_enabled 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            <span className={`w-2 h-2 rounded-full mr-2 ${
              status?.is_enabled ? 'bg-green-500' : 'bg-red-500'
            }`}></span>
            {status?.is_enabled ? 'Enabled' : 'Disabled'}
          </div>
        </div>

        {status?.is_enabled ? (
          <div className="space-y-4">
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-start">
                <span className="text-green-600 mr-3">✅</span>
                <div>
                  <h4 className="font-medium text-green-900">2FA is Active</h4>
                  <p className="text-sm text-green-800 mt-1">
                    Your account is protected with two-factor authentication.
                    {status.last_used_at && (
                      <span className="block">
                        Last used: {new Date(status.last_used_at).toLocaleString()}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">Backup Codes</p>
                <p className="text-sm text-gray-600">
                  {status.backup_tokens_count} codes remaining
                </p>
              </div>
              <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                Generate New Codes
              </button>
            </div>

            <button
              onClick={startDisable}
              className="w-full px-4 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
              disabled={loading}
            >
              Disable Two-Factor Authentication
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-start">
                <span className="text-yellow-600 mr-3">⚠️</span>
                <div>
                  <h4 className="font-medium text-yellow-900">Security Recommendation</h4>
                  <p className="text-sm text-yellow-800 mt-1">
                    Enable 2FA to add an extra layer of security to your account. 
                    This helps protect against unauthorized access even if your password is compromised.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={startSetup}
              className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              disabled={loading}
            >
              Enable Two-Factor Authentication
            </button>
          </div>
        )}
      </div>

      {/* Disable confirmation modal */}
      {showDisableForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-red-600 text-xl">⚠️</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Disable Two-Factor Authentication?
              </h3>
              <p className="text-sm text-gray-600">
                This will make your account less secure. You'll need to verify your identity to continue.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your password"
                />
              </div>

              <TwoFactorVerifyForm
                onSuccess={(method) => {
                  // Handle the verification and then call disable
                  handleDisable(disablePassword, method === 'totp' ? '123456' : undefined, method === 'backup' ? 'ABC12345' : undefined);
                }}
                onError={setError}
                showBackupOption={true}
                className="border-t pt-4"
              />
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={cancelAction}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Information Section */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
          <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            ℹ️
          </span>
          About Two-Factor Authentication
        </h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>Two-factor authentication (2FA) adds an extra layer of security to your account by requiring both your password and a temporary code from your mobile device.</p>
          <p><strong>Benefits:</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>Protects against password theft and phishing attacks</li>
            <li>Prevents unauthorized access even if your password is compromised</li>
            <li>Provides backup codes for emergency access</li>
            <li>Industry-standard security practice</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
