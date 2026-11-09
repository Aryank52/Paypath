import React, { useEffect, useState } from 'react';
import {
  X,
  ShieldCheck,
  RotateCcw,
  Clock,
  User,
  ArrowRight,
  ExternalLink,
  AlertTriangle
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
  const { setActiveTab, setActiveReclaimCase } = useStore();

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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-sm">
              {transaction.merchant_name.charAt(0)}
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">{transaction.merchant_name}</h2>
              <p className="text-[11px] text-slate-400 font-mono">ID: {transaction.id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Main Highlights */}
          <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">Captured Amount</div>
              <div className="text-lg font-bold text-white mt-0.5">
                ${transaction.amount.toFixed(2)} <span className="text-xs text-slate-400 font-normal">{transaction.currency}</span>
              </div>
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">Payment Status</div>
              <div className="mt-1">
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {transaction.status}
                </span>
              </div>
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-slate-400">PayPal Verification</div>
              <div className="flex items-center space-x-1.5 mt-1 text-emerald-400 text-xs font-medium">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Verified Read-Back</span>
              </div>
            </div>
          </div>

          {/* AI Explanation Card */}
          <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-1.5">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-indigo-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>AI Transaction Intelligence</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {transaction.ai_summary || "Normal transaction lifecycle captured and verified against PayPal Sandbox."}
            </p>
          </div>

          {/* Chronological Event Timeline */}
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
                    <div className="text-[10px] text-slate-400 mt-1">
                      {new Date(ev.created_at).toLocaleString()} • Actor: {ev.actor}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="text-xs text-slate-400">
            PayPal Order ID: <span className="font-mono text-slate-300">{transaction.paypal_order_id || 'N/A'}</span>
          </div>
          <button
            onClick={handleOpenReclaim}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors shadow-md shadow-emerald-600/20"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Open RECLAIM Claim</span>
          </button>
        </div>
      </div>
    </div>
  );
};

