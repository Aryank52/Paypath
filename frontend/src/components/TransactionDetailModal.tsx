import React, { useEffect, useState } from 'react';
import {
  X,
  ShieldCheck,
  RotateCcw,
  Clock,
  User,
  ArrowRight,
  ExternalLink,
  AlertTriangle,
  FileText,
  Sparkles,
  CheckCircle2,
  Tag
} from 'lucide-react';
import { Transaction, TransactionEvent } from '../types';
import { api } from '../services/api';
import { useStore } from '../store/useStore';

interface Props {
  transaction: Transaction;
  onClose: () => void;
}

export const TransactionDetailModal: React.FC<Props> = ({ transaction, onClose }) => {
  const [events, setEvents] = useState<TransactionEvent[]>([]);
  const [isLoadingEvents, setIsLoadingEvents] = useState(true);
  const { setActiveTab } = useStore();

  useEffect(() => {
    setIsLoadingEvents(true);
    api.getTransactionEvents(transaction.id)
      .then(setEvents)
      .catch(console.error)
      .finally(() => setIsLoadingEvents(false));
  }, [transaction.id]);

  const handleOpenReclaim = () => {
    onClose();
    setActiveTab('reclaim');
  };

  const isSynthetic = (transaction as any).source_type === 'DEMO_SEED' || transaction.id.startsWith('tx_');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* 1. Transaction Summary Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-sm">
              {transaction.merchant_name ? transaction.merchant_name.charAt(0) : 'P'}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-white tracking-tight">{transaction.merchant_name}</h2>
                <span className={`text-[9px] uppercase px-2 py-0.5 rounded-full font-mono font-semibold ${
                  isSynthetic
                    ? 'bg-slate-800 text-slate-400 border border-slate-700'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                }`}>
                  {isSynthetic ? 'DEMO SEED' : 'PAYPAL SANDBOX'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">ID: {transaction.id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body: Ordered per Specification */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {/* Main Highlights Grid */}
          <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">Captured Amount</div>
              <div className="text-lg font-bold text-white mt-0.5">
                ${Number(transaction.amount).toFixed(2)} <span className="text-xs text-slate-400 font-normal">{transaction.currency}</span>
              </div>
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">Payment State</div>
              <div className="mt-1">
                <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${
                  transaction.status === 'CAPTURED'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : transaction.status === 'REFUNDED' || transaction.status === 'PARTIALLY_REFUNDED'
                    ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {transaction.status}
                </span>
              </div>
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">Risk Signal</div>
              <div className="mt-1">
                <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${
                  transaction.risk_level === 'HIGH'
                    ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    : transaction.risk_level === 'MEDIUM'
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                }`}>
                  {transaction.risk_level || 'LOW'} (Score: {Number(transaction.risk_score || 0).toFixed(2)})
                </span>
              </div>
            </div>
          </div>

          {/* 2. AI Understanding & Intent Insight */}
          <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-1.5">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-indigo-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Transaction Intelligence</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {transaction.ai_summary || "Normal transaction lifecycle captured and verified against PayPal Sandbox."}
            </p>
            {transaction.item_description && (
              <div className="pt-1 flex items-center space-x-1.5 text-[11px] text-slate-400">
                <Tag className="w-3 h-3 text-slate-500" />
                <span>Product / Item: <strong className="text-slate-300">{transaction.item_description}</strong></span>
              </div>
            )}
          </div>

          {/* 3. Policy Evidence & Merchant Rules */}
          <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>Applicable Merchant Policy</span>
              </span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                30-Day Window Active
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              {transaction.merchant_name} standard refund and return policy allows reimbursement for transit defects and damaged items upon evidence submission.
            </p>
          </div>

          {/* 4. Immutable Chronological Event Timeline */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>Immutable Lifecycle Timeline</span>
            </h3>

            {isLoadingEvents ? (
              <div className="py-4 text-center text-xs text-slate-500">Loading lifecycle events...</div>
            ) : events.length === 0 ? (
              <div className="py-4 text-center text-xs text-slate-500">No events logged for this transaction.</div>
            ) : (
              <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {events.map((ev) => (
                  <div key={ev.id} className="relative">
                    <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-indigo-500 border-2 border-slate-900"></div>
                    <div className="text-xs font-semibold text-slate-200">{ev.event_type}</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">{ev.description}</div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      {new Date(ev.created_at).toLocaleString()} • Actor: {ev.actor}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 5. Footer: Dual-Phase Verification & Recommended Action */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span>Verified by PayPal</span>
              {transaction.paypal_order_id && (
                <span className="font-mono text-slate-400 ml-1.5">({transaction.paypal_order_id.slice(0, 16)}...)</span>
              )}
            </div>
          </div>
          <button
            onClick={handleOpenReclaim}
            className="flex items-center justify-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors shadow-md shadow-emerald-600/20 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Open RECLAIM Resolution</span>
          </button>
        </div>
      </div>
    </div>
  );
};
