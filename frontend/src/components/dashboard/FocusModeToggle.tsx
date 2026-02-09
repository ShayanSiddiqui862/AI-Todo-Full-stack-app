'use client';

import React, { useState, useEffect } from 'react';

const FocusModeToggle = () => {
  const [isFocusMode, setIsFocusMode] = useState(false);

  // Load focus mode preference from localStorage
  useEffect(() => {
    const savedFocusMode = localStorage.getItem('focusMode');
    if (savedFocusMode) {
      setIsFocusMode(savedFocusMode === 'true');
    }
  }, []);

  // Apply focus mode styles to the document
  useEffect(() => {
    if (isFocusMode) {
      document.body.classList.add('focus-mode');
    } else {
      document.body.classList.remove('focus-mode');
    }

    // Save preference to localStorage
    localStorage.setItem('focusMode', isFocusMode.toString());
  }, [isFocusMode]);

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-400">Focus Mode</span>
      <button
        onClick={() => setIsFocusMode(!isFocusMode)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
          isFocusMode ? 'bg-linear-to-r from-blue-500 to-purple-500' : 'bg-gray-700'
        }`}
        aria-label="Toggle focus mode"
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            isFocusMode ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
};

export default FocusModeToggle;