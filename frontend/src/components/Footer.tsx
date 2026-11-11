import React from 'react';
import { ShieldCheck, Activity, ExternalLink } from 'lucide-react';
import { useStore } from '../store/useStore';

export const Footer: React.FC = () => {
  const { setLegalModal, setActiveTab, isAuthenticated } = useStore();

  return (
    <footer className="bg-slate-950 border-t border-slate-900 py-12 px-6 sm:px-12 lg:px-20 text-slate-400 text-xs font-sans">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        {/* Brand Column */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <span className="font-bold text-sm tracking-wider text-white">PAYPATH</span>
          </div>
          <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
            AI Transaction Intelligence & Agentic Commerce platform. Ensuring policy-aware payments, deterministic protection, and verified dispute resolution.
          </p>
          <div className="text-[11px] text-slate-500 font-mono">
            Understand. Decide. Act. Verify.
          </div>
        </div>

        {/* Product Navigation */}
        <div className="space-y-2.5">
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider block mb-2">Platform</span>
          <div>
            <button
              onClick={() => setActiveTab(isAuthenticated ? 'overview' : 'landing')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Overview & Dashboard
            </button>
          </div>
          <div>
            <button
              onClick={() => setActiveTab(isAuthenticated ? 'transactions' : 'landing')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Transaction Intelligence
            </button>
          </div>
          <div>
            <button
              onClick={() => setActiveTab(isAuthenticated ? 'guard' : 'landing')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Payment Guard Pre-Check
            </button>
          </div>
          <div>
            <button
              onClick={() => setActiveTab(isAuthenticated ? 'reclaim' : 'landing')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              RECLAIM Dispute Resolution
            </button>
          </div>
          <div>
            <button
              onClick={() => setActiveTab(isAuthenticated ? 'shopping' : 'landing')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Safe Agentic Commerce
            </button>
          </div>
        </div>

        {/* Trust & Legal */}
        <div className="space-y-2.5">
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider block mb-2">Trust & Security</span>
          <div>
            <button
              onClick={() => setLegalModal('privacy')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Privacy Policy
            </button>
          </div>
          <div>
            <button
              onClick={() => setLegalModal('terms')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Terms of Service
            </button>
          </div>
          <div>
            <a
              href="/api/v1/system/health"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors inline-flex items-center gap-1"
            >
              <Activity className="w-3 h-3 text-emerald-400" />
              <span>System Health & Status</span>
            </a>
          </div>
          <div className="text-[11px] text-slate-500 pt-2">
            Authoritative DB: PostgreSQL 16
            <br />
            Payment Gateway: PayPal Sandbox
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-900/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <span>© 2026 PayPath Technologies Inc. All rights reserved.</span>
        <div className="flex items-center gap-6">
          <button onClick={() => setLegalModal('privacy')} className="hover:text-slate-300 transition-colors cursor-pointer">Privacy</button>
          <button onClick={() => setLegalModal('terms')} className="hover:text-slate-300 transition-colors cursor-pointer">Terms</button>
          <a href="/robots.txt" className="hover:text-slate-300 transition-colors">Robots</a>
          <a href="/sitemap.xml" className="hover:text-slate-300 transition-colors">Sitemap</a>
        </div>
      </div>
    </footer>
  );
};
