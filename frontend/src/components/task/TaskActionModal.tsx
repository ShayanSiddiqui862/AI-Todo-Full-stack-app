'use client';

import React, { useState } from 'react';

interface TaskActionModalProps {
  isOpen: boolean;
  taskTitle: string;
  onClose: () => void;
  onComplete: () => void;
  onDelay: (minutes: number) => void;
}

const TaskActionModal: React.FC<TaskActionModalProps> = ({
  isOpen,
  taskTitle,
  onClose,
  onComplete,
  onDelay,
}) => {
  const [showDelayOptions, setShowDelayOptions] = useState(false);
  const [customMinutes, setCustomMinutes] = useState('');

  if (!isOpen) return null;

  const handleDelayClick = (minutes: number) => {
    onDelay(minutes);
    setShowDelayOptions(false);
    onClose();
  };

  const handleCustomDelay = () => {
    const minutes = parseInt(customMinutes, 10);
    if (minutes > 0) {
      handleDelayClick(minutes);
    }
  };

  const handleComplete = () => {
    onComplete();
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div 
        className="bg-gray-900/95 border border-white/10 rounded-2xl p-6 w-full max-w-sm mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-lg font-semibold text-white mb-2 truncate">{taskTitle}</h3>
        <p className="text-gray-400 text-sm mb-6">What would you like to do?</p>

        {!showDelayOptions ? (
          <div className="space-y-3">
            <button
              onClick={handleComplete}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              Mark Completed
            </button>
            
            <button
              onClick={() => setShowDelayOptions(true)}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 text-white font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Delay Task
            </button>

            <button
              onClick={onClose}
              className="w-full py-3 px-4 rounded-xl bg-white/5 border border-white/10 text-gray-300 font-medium hover:bg-white/10 transition-all"
            >
              Cancel
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-gray-300 text-sm font-medium mb-3">Delay by:</p>
            
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handleDelayClick(15)}
                className="py-2 px-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-all text-sm"
              >
                15 min
              </button>
              <button
                onClick={() => handleDelayClick(30)}
                className="py-2 px-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-all text-sm"
              >
                30 min
              </button>
              <button
                onClick={() => handleDelayClick(60)}
                className="py-2 px-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-all text-sm"
              >
                1 hour
              </button>
              <button
                onClick={() => handleDelayClick(120)}
                className="py-2 px-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-all text-sm"
              >
                2 hours
              </button>
            </div>

            <div className="flex gap-2 mt-3">
              <input
                type="number"
                value={customMinutes}
                onChange={(e) => setCustomMinutes(e.target.value)}
                placeholder="Custom mins"
                min="1"
                className="flex-1 px-3 py-2 bg-black/30 border border-white/10 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              <button
                onClick={handleCustomDelay}
                disabled={!customMinutes || parseInt(customMinutes, 10) <= 0}
                className="px-4 py-2 rounded-lg bg-orange-500 text-white text-sm hover:bg-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Set
              </button>
            </div>

            <button
              onClick={() => setShowDelayOptions(false)}
              className="w-full py-2 px-4 rounded-lg bg-white/5 text-gray-400 text-sm hover:bg-white/10 transition-all mt-2"
            >
              ← Back
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskActionModal;
