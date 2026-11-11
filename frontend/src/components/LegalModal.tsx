import React from 'react';
import { X, FileText, Lock, ShieldCheck, Scale, RefreshCw } from 'lucide-react';
import { useStore } from '../store/useStore';

export const LegalModal: React.FC = () => {
  const { legalModal, setLegalModal } = useStore();

  if (!legalModal) return null;

  const getTitleAndIcon = () => {
    switch (legalModal) {
      case 'privacy':
        return { title: 'Privacy Policy', icon: <Lock className="w-5 h-5 text-indigo-400" /> };
      case 'terms':
        return { title: 'Terms of Service', icon: <FileText className="w-5 h-5 text-emerald-400" /> };
      case 'dpdp':
        return { title: 'India DPDP Act 2023 & Grievance Redressal', icon: <Scale className="w-5 h-5 text-sky-400" /> };
      case 'refund':
        return { title: 'RECLAIM Refund & Settlement Policy', icon: <RefreshCw className="w-5 h-5 text-amber-400" /> };
      case 'security':
        return { title: 'Security Architecture & Controls', icon: <ShieldCheck className="w-5 h-5 text-emerald-400" /> };
      default:
        return { title: 'Platform Information', icon: <FileText className="w-5 h-5 text-slate-400" /> };
    }
  };

  const { title, icon } = getTitleAndIcon();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2.5">
            {icon}
            <h2 className="text-base font-bold text-white tracking-tight">{title}</h2>
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
          {legalModal === 'privacy' && (
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
          )}

          {legalModal === 'terms' && (
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

          {legalModal === 'dpdp' && (
            <>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">1. Statutory Rights of the Data Principal</h3>
                <p>
                  In compliance with the Digital Personal Data Protection (DPDP) Act 2023, you have the right to access a summary
                  of personal data processed by PayPath, request correction of inaccurate data, and demand erasure of personal data
                  subject to statutory record-retention requirements under applicable financial regulations.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">2. Grievance Redressal Mechanism (Section 13)</h3>
                <p>
                  If you have concerns regarding data processing or privacy rights, you may submit a formal complaint to our designated Grievance Officer:
                </p>
                <div className="mt-2 p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300">
                  <div><strong>Designation:</strong> Data Protection & Grievance Redressal Officer</div>
                  <div><strong>Email:</strong> grievance@paypath.finance</div>
                  <div><strong>Jurisdiction:</strong> Republic of India</div>
                  <div><strong>Response Window:</strong> Within 30 calendar days</div>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">3. Security Safeguards & Breach Protocol</h3>
                <p>
                  PayPath implements reasonable security safeguards (bcrypt password hashing, TLS 1.3 transport encryption, role-based access control,
                  and tenant data isolation). In the event of a personal data breach, PayPath will notify the Data Protection Board of India
                  and affected data principals in accordance with DPDP regulations within 72 hours.
                </p>
              </div>
            </>
          )}

          {legalModal === 'refund' && (
            <>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">1. Deterministic Policy Superiority</h3>
                <p>
                  PayPath enforces the core architectural invariant: <em>Deterministic merchant policy always overrides stochastic AI suggestions</em>.
                  Refunds are evaluated against the specific merchant's verified return window, defect clauses, and proof requirements.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">2. Multimodal Evidence Grounding</h3>
                <p>
                  Dispute cases require photographic or receipt evidence. AI vision models classify evidence confidence, which is then
                  matched against verbatim merchant clauses indexed in the PostgreSQL RAG vector store.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">3. Dual-Phase Settlement Read-Back</h3>
                <p>
                  Upon refund initiation, PayPath transmits a refund mutation with an idempotency key to PayPal REST v2.
                  The transaction status only updates to <code>REFUNDED / VERIFIED</code> after an independent out-of-band read-back
                  to PayPal's <code>/v2/payments/refunds/{'{id}'}</code> endpoint confirms successful settlement.
                </p>
              </div>
            </>
          )}

          {legalModal === 'security' && (
            <>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">1. 78-Control Security Baseline</h3>
                <p>
                  PayPath operates under an audited 78-control security baseline encompassing multi-factor authentication (MFA TOTP),
                  Bcrypt 12-round hashing, strict CORS origin whitelisting, SSRF-protected PayPal certificate validation, and zero unauthenticated route access in production.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">2. PCI-DSS Scoping Guarantee</h3>
                <p>
                  PayPath never collects, stores, or processes unencrypted credit card numbers, CVVs, or cardholder credentials.
                  All payment actions utilize tokenized PayPal order and capture IDs.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-1">3. Immutable Audit Trails</h3>
                <p>
                  Every administrative access, policy upload, transaction creation, and refund mutation is immutably logged
                  with user ID, actor type, IP address, and payload delta in the authoritative PostgreSQL <code>audit_logs</code> table.
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">Effective Date: November 2026 • Version 1.0.0</span>
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
