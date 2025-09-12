"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';

interface LandingToggleProps {
  currentMode: 'classic' | 'progressive';
  onModeChange: (mode: 'classic' | 'progressive') => void;
}

export default function LandingToggle({ currentMode, onModeChange }: LandingToggleProps) {
  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-lg p-1 shadow-lg">
        <div className="flex items-center space-x-1">
          <motion.button
            onClick={() => onModeChange('classic')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              currentMode === 'classic'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Classic Demo
          </motion.button>
          <motion.button
            onClick={() => onModeChange('progressive')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              currentMode === 'progressive'
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            ✨ Progressive Flow
          </motion.button>
        </div>
      </div>
    </div>
  );
}
