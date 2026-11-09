import React, { useEffect, useState } from 'react';
import { Repeat, AlertTriangle, CheckCircle2, RotateCcw, Calendar, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { DuplicateSignal, SubscriptionItem } from '../types';
import { useStore } from '../store/useStore';

export const RecoveryIntelligence: React.FC = () => {
  const [duplicates, setDuplicates] = useState<DuplicateSignal[]>([]);
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { setActiveTab } = useStore();

  useEffect(() => {
    setIsLoading(true);
    Promise.all([api.getDuplicates(), api.getSubscriptions()])
      .then(([dups, subs]) => {
        setDuplicates(dups);
        setSubscriptions(subs);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>Payment Recovery Intelligence</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Mode 4 — Recover
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Detect duplicate charges, monitor subscription intervals, and recover revenue from unresolved payment exceptions.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Duplicate Signals Column */}
        <div className="md:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>Suspected Duplicate Charges</span>
            </h2>
            <span className="text-[10px] text-amber-400 font-semibold">{duplicates.length} Detected</span>
          </div>

          {isLoading ? (
            <div className="p-8 text-center text-xs text-slate-500">Scanning transactions...</div>
          ) : duplicates.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-400">
              No duplicate charges detected.
            </div>
          ) : (
            <div className="space-y-3">
              {duplicates.map((dup, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-amber-500/30 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-xs font-bold text-white">{dup.merchant_name}</div>
                      <div className="text-[11px] text-amber-400 font-medium">{dup.signal_type}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-white">${dup.amount.toFixed(2)}</div>
                      <div className="text-[10px] text-slate-400">{dup.currency}</div>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                    {dup.explanation}
                  </p>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-slate-400">Confidence: {int(dup.confidence_score * 100)}%</span>
                    <button
                      onClick={() => setActiveTab('reclaim')}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all flex items-center space-x-1"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>One-Click Duplicate Refund</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Subscriptions Tracker Column */}
        <div className="md:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Calendar className="w-3.5 h-3.5 text-indigo-400" />
              <span>Active Recurring Payments</span>
            </h2>
          </div>

          <div className="space-y-3">
            {subscriptions.map((sub) => (
              <div key={sub.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold text-white">{sub.merchant_name}</div>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {sub.billing_interval}
                  </span>
                </div>
                <div className="text-lg font-bold text-white">
                  ${sub.amount.toFixed(2)} <span className="text-xs text-slate-400 font-normal">/ month</span>
                </div>
                <div className="text-[11px] text-slate-400 space-y-0.5">
                  <div>Last Payment: {sub.last_payment_date}</div>
                  <div>Next Expected: <span className="text-indigo-300 font-medium">{sub.next_expected_date}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

function int(val: number): number {
  return Math.round(val);
}
