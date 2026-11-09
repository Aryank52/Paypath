import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  ArrowUpRight,
  Sparkles,
  ShoppingBag,
  ExternalLink
} from 'lucide-react';
import { useStore } from '../store/useStore';
import { api } from '../services/api';
import { Transaction } from '../types';

export const OverviewDashboard: React.FC = () => {
  const { setActiveTab, setSelectedTransaction } = useStore();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.getTransactions()
      .then(setTransactions)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const totalVolume = transactions.reduce((acc, tx) => acc + tx.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Financial Intelligence Control Center</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time policy guardrails, PayPal Sandbox tracking, and post-purchase dispute recovery.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('shopping')}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-md shadow-indigo-600/20"
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>New Guarded Purchase</span>
          </button>
          <button
            onClick={() => setActiveTab('reclaim')}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors shadow-md shadow-emerald-600/20"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Open RECLAIM Claim</span>
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Tracked Volume</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white tracking-tight">
            ${totalVolume.toFixed(2)}
          </div>
          <div className="mt-1 text-[11px] text-slate-400 flex items-center space-x-1">
            <span className="text-emerald-400 font-medium">3 Transactions</span>
            <span>in sandbox ledger</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Active Safeguards</span>
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white tracking-tight">
            4 Rules
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            $100 spend cap & restricted categories
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Attention Required</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-amber-400 tracking-tight">
            1 Dispute
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            NovaSound damaged item ($65 refund)
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Verified Recoveries</span>
            <RotateCcw className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-400 tracking-tight">
            100% Verified
          </div>
          <div className="mt-1 text-[11px] text-slate-400">
            Dual-phase PayPal read-back audit
          </div>
        </div>
      </div>

      {/* Hero Alert Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/60 to-slate-900/80 border border-indigo-500/30 flex items-center justify-between">
        <div className="flex items-start space-x-3.5">
          <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 mt-0.5">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">RECLAIM Resolution Ready for Review</h3>
            <p className="text-xs text-slate-300 mt-0.5 max-w-2xl leading-relaxed">
              Photographic evidence confirmed structural damage on Nova Electronics transaction (<span className="text-indigo-300 font-mono">5O190127...</span>).
              RAG policy analysis recommends a <strong className="text-white">$65.00 partial refund</strong> adhering to the 30-day return policy.
            </p>
          </div>
        </div>
        <button
          onClick={() => setActiveTab('reclaim')}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/30 transition-all flex items-center space-x-1.5 whitespace-nowrap"
        >
          <span>Review & Approve</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Recent Transactions Table Preview */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-semibold text-white">Recent Transactions</h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
              Live Feed
            </span>
          </div>
          <button
            onClick={() => setActiveTab('transactions')}
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
          >
            <span>Open AG Grid Explorer</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading transactions...</div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {transactions.map((tx) => (
              <div
                key={tx.id}
                onClick={() => {
                  setSelectedTransaction(tx);
                  setActiveTab('transactions');
                }}
                className="py-3 px-2 flex items-center justify-between hover:bg-slate-800/40 rounded-lg cursor-pointer transition-colors"
              >
                <div className="flex items-center space-x-3.5">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-slate-300">
                    {tx.merchant_name.charAt(0)}
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-200">{tx.merchant_name}</div>
                    <div className="text-[11px] text-slate-400">{tx.item_description}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  {/* AI Insight Pill */}
                  <div className="hidden lg:block text-right max-w-xs">
                    <span className="text-[11px] text-slate-400 line-clamp-1">{tx.ai_summary}</span>
                  </div>

                  {/* Verification Status */}
                  <div>
                    <span
                      className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full ${
                        tx.verification_status === 'VERIFIED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {tx.verification_status === 'VERIFIED' ? 'Verified by PayPal' : tx.verification_status}
                    </span>
                  </div>

                  {/* Amount */}
                  <div className="text-right min-w-[70px]">
                    <div className="text-xs font-bold text-white">${tx.amount.toFixed(2)}</div>
                    <div className="text-[10px] text-slate-400">{tx.currency}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

