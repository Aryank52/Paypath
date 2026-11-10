import React from 'react';
import { X, FileText, Lock } from 'lucide-react';
import { useStore } from '../store/useStore';

export const LegalModal: React.FC = () => {
  const { legalModal, setLegalModal } = useStore();

  if (!legalModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2.5">
            {legalModal === 'privacy' ? (
              <Lock className="w-5 h-5 text-indigo-400" />
            ) : (
              <FileText className="w-5 h-5 text-emerald-400" />
            )}
            <h2 className="text-base font-bold text-white tracking-tight">
              {legalModal === 'privacy' ? 'Privacy Policy' : 'Terms of Service'}
            </h2>
          </div>
          <button
            onClick={() => setLegalModal(null)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto text-xs text-slate-300 leading-relaxed">
          {legalModal === 'privacy' ? (
            <>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">1. Information We Collect</h3>
                <p>
                  PayPath processes payment telemetry strictly necessary to execute and verify transaction intelligence,
                  guarded commerce, and post-purchase resolution. Financial mutations are mediated directly through PayPal.
                  We do not store raw credit card numbers or banking passwords.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">2. AI & Data Privacy</h3>
                <p>
                  AI models operate on sanitized transaction metadata, merchant policy documents, and customer dispute descriptions.
                  Customer financial records are never used to train public LLM foundations without explicit consent.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">3. Tenant Isolation & Multi-Tenancy</h3>
                <p>
                  Merchant policies, embeddings, and transaction logs are logically partitioned by tenant ID to prevent cross-tenant data leakage.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">4. Cookies & Local Storage</h3>
                <p>
                  PayPath uses essential functional tokens (JWT authentication, persona state) for session management.
                  No non-essential third-party advertising tracking cookies are installed.
                </p>
              </div>
            </>
          ) : (
            <>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">1. Acceptance of Terms</h3>
                <p>
                  By accessing PayPath, you agree to these Terms of Service. PayPath provides AI-assisted transaction monitoring,
                  pre-purchase policy checks, and post-purchase RECLAIM facilitation.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">2. Non-Authoritative AI Advisory</h3>
                <p>
                  PayPath AI recommendations, risk scores, and policy interpretations are advisory signals designed to support human decisions.
                  All consequential financial operations (such as refunds or captures) are governed by deterministic policy rules
                  and require explicit human or merchant authorization where configured.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">3. PayPal Sandbox & Settlement</h3>
                <p>
                  In sandbox and staging environments, transactions are processed against the PayPal Sandbox API.
                  No real-money funds are captured.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">4. Audit & Dispute Resolution</h3>
                <p>
                  All mutations generate immutable audit logs and dual-phase verification records. Users may contest findings
                  via the RECLAIM Resolution Center.
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">Effective Date: November 2026 • Version 1.0</span>
          <button
            onClick={() => setLegalModal(null)}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors cursor-pointer"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
};
