import React, { useState, useEffect } from 'react';
import { ShieldCheck, X } from 'lucide-react';
import { useStore } from '../store/useStore';

export const CookieBanner: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const { setLegalModal } = useStore();

  useEffect(() => {
    const dismissed = localStorage.getItem('paypath_storage_consent_dismissed');
    if (!dismissed) {
      setVisible(true);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem('paypath_storage_consent_dismissed', 'true');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-40 max-w-md p-4 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl shadow-2xl text-xs text-slate-300 animate-in fade-in slide-in-from-bottom-3 duration-300">
      <div className="flex items-start space-x-3">
        <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 shrink-0 mt-0.5">
          <ShieldCheck className="w-4 h-4" />
        </div>
        <div className="flex-1 space-y-1.5">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-white text-xs">Essential Storage & Privacy Notice</h4>
            <button
              onClick={handleDismiss}
              className="text-slate-400 hover:text-slate-200 transition-colors p-0.5"
              aria-label="Dismiss"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-400">
            PayPath utilizes strictly essential local storage tokens for JWT session authentication and role state.
            We do not deploy advertising, telemetry, or cross-site tracking cookies.
          </p>
          <div className="flex items-center space-x-3 pt-1">
            <button
              onClick={handleDismiss}
              className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-[11px] font-medium transition-colors cursor-pointer shadow-sm shadow-indigo-500/20"
            >
              Acknowledge
            </button>
            <button
              onClick={() => setLegalModal('privacy')}
              className="text-[11px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors cursor-pointer"
            >
              Privacy Policy
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
