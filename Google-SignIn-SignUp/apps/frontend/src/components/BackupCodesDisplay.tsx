"use client";

import React, { useState } from "react";
import { BackupCodesDisplayProps } from "../lib/types";

export const BackupCodesDisplay: React.FC<BackupCodesDisplayProps> = ({
  codes,
  onDownload,
  onClose,
  className = "",
}) => {
  const [copied, setCopied] = useState(false);

  const copyAllCodes = async () => {
    try {
      const codesText = codes.map((code, index) => `${index + 1}. ${code}`).join('\n');
      await navigator.clipboard.writeText(codesText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy codes:", err);
    }
  };

  const downloadCodes = () => {
    const codesText = [
      "Two-Factor Authentication Backup Codes",
      "Generated on: " + new Date().toLocaleString(),
      "",
      "IMPORTANT: Keep these codes in a safe place!",
      "Each code can only be used once.",
      "",
      ...codes.map((code, index) => `${index + 1}. ${code}`),
      "",
      "If you lose access to your authenticator app, you can use",
      "these backup codes to regain access to your account.",
    ].join('\n');

    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backup-codes-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    onDownload?.();
  };

  const printCodes = () => {
    const printContent = `
      <html>
        <head>
          <title>Two-Factor Authentication Backup Codes</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; }
            .codes { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; }
            .code { padding: 10px; border: 1px solid #ccc; text-align: center; font-family: monospace; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Two-Factor Authentication Backup Codes</h1>
            <p>Generated on: ${new Date().toLocaleString()}</p>
          </div>
          <div class="warning">
            <strong>IMPORTANT:</strong> Keep these codes in a safe place!<br>
            Each code can only be used once to access your account if you lose your authenticator device.
          </div>
          <div class="codes">
            ${codes.map((code, index) => `<div class="code">${index + 1}. ${code}</div>`).join('')}
          </div>
          <p><strong>Instructions:</strong></p>
          <ul>
            <li>Store these codes in a secure location</li>
            <li>Do not share these codes with anyone</li>
            <li>Each code can only be used once</li>
            <li>Generate new codes if you use all of these</li>
          </ul>
        </body>
      </html>
    `;
    
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(printContent);
      printWindow.document.close();
      printWindow.print();
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl">✅</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Two-Factor Authentication Enabled!
        </h2>
        <p className="text-gray-600">
          Save these backup codes in a secure location
        </p>
      </div>

      {/* Important Warning */}
      <div className="bg-red-50 rounded-lg p-4 border border-red-200">
        <div className="flex items-start">
          <span className="text-red-600 mr-3 text-xl">🚨</span>
          <div>
            <h3 className="font-semibold text-red-900 mb-2">Critical: Save These Codes Now</h3>
            <div className="text-sm text-red-800 space-y-1">
              <p>• These backup codes are your only way to access your account if you lose your authenticator device</p>
              <p>• Each code can only be used once</p>
              <p>• We won't show these codes again</p>
              <p>• Store them in a secure password manager or print them out</p>
            </div>
          </div>
        </div>
      </div>

      {/* Backup Codes Grid */}
      <div className="bg-white rounded-xl shadow-lg border p-6">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
          <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            📝
          </span>
          Your Backup Codes
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
          {codes.map((code, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
            >
              <span className="text-sm text-gray-600 font-medium">
                {index + 1}.
              </span>
              <code className="font-mono text-lg font-semibold text-gray-900 tracking-wider">
                {code}
              </code>
              <div className="w-6"></div> {/* Spacer for alignment */}
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={downloadCodes}
            className="flex-1 flex items-center justify-center px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            <span className="mr-2">💾</span>
            Download as Text File
          </button>
          
          <button
            onClick={copyAllCodes}
            className="flex-1 flex items-center justify-center px-4 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
          >
            <span className="mr-2">{copied ? "✅" : "📋"}</span>
            {copied ? "Copied!" : "Copy All Codes"}
          </button>
          
          <button
            onClick={printCodes}
            className="flex-1 flex items-center justify-center px-4 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
          >
            <span className="mr-2">🖨️</span>
            Print Codes
          </button>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
          <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            ℹ️
          </span>
          How to Use Backup Codes
        </h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p><strong>When to use:</strong> Use these codes if you lose access to your authenticator app or device.</p>
          <p><strong>How to use:</strong> During login, choose "Use backup code" and enter one of these codes.</p>
          <p><strong>After use:</strong> Each code becomes invalid after use. Generate new codes when you're running low.</p>
        </div>
      </div>

      {/* Storage Recommendations */}
      <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
        <h3 className="font-semibold text-yellow-900 mb-3 flex items-center">
          <span className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center text-white text-sm mr-2">
            💡
          </span>
          Recommended Storage Options
        </h3>
        <div className="text-sm text-yellow-800 space-y-1">
          <p>• <strong>Password Manager:</strong> Store in a secure note in your password manager</p>
          <p>• <strong>Secure Note App:</strong> Use an encrypted note-taking app</p>
          <p>• <strong>Physical Copy:</strong> Print and store in a secure location (safe, lockbox)</p>
          <p>• <strong>Encrypted File:</strong> Save in an encrypted file on a secure device</p>
        </div>
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onClose}
          className="px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
        >
          I've Saved My Backup Codes
        </button>
      </div>

      {/* Final Warning */}
      <div className="text-center">
        <p className="text-sm text-gray-500">
          Make sure you've saved these codes before continuing.{" "}
          <strong className="text-gray-700">You won't be able to see them again.</strong>
        </p>
      </div>
    </div>
  );
};
