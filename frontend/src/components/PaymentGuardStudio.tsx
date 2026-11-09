import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Sliders, CheckCircle2, Play, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { GuardEvaluation } from '../types';

export const PaymentGuardStudio: React.FC = () => {
  const [amount, setAmount] = useState(89.0);
  const [merchant, setMerchant] = useState('Nova Electronics');
  const [category, setCategory] = useState('electronics');
  const [simulationResult, setSimulationResult] = useState<GuardEvaluation | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await api.evaluateGuard({
        amount,
        merchant_name: merchant,
        category
      });
      setSimulationResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>Payment Guard Studio</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Deterministic Engine
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure spending limits, approval triggers, and restricted categories. Test any transaction in the simulation sandbox.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Policy Configuration Controls */}
        <div className="md:col-span-6 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>Active Spending Policies</span>
            </h2>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>Max Per-Transaction Spend Cap</span>
                  <span className="font-bold text-white">$300.00</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="1000"
                  defaultValue="300"
                  className="w-full accent-indigo-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>Auto-Approval Limit (Above triggers Human Gate)</span>
                  <span className="font-bold text-white">$50.00</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="200"
                  defaultValue="50"
                  className="w-full accent-emerald-500 cursor-pointer"
                />
              </div>

              <div className="pt-2 border-t border-slate-800 space-y-2">
                <div className="text-xs font-semibold text-slate-300">Restricted Safety Categories</div>
                <div className="flex flex-wrap gap-1.5">
                  {['Gambling', 'Crypto', 'Weapons', 'High-Risk Dropship'].map((cat) => (
                    <span
                      key={cat}
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20"
                    >
                      {cat} (Blocked)
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Transaction Simulator Sandbox */}
        <div className="md:col-span-6 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Play className="w-3.5 h-3.5 text-emerald-400" />
              <span>Transaction Simulation Sandbox</span>
            </h2>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Proposed Amount ($)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Merchant Name</label>
                <input
                  type="text"
                  value={merchant}
                  onChange={(e) => setMerchant(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="electronics">Electronics (Allowed)</option>
                  <option value="apparel">Apparel (Allowed)</option>
                  <option value="travel">Travel (Allowed)</option>
                  <option value="gambling">Gambling (Prohibited)</option>
                </select>
              </div>

              <button
                onClick={handleSimulate}
                disabled={isSimulating}
                className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/30 transition-all flex items-center justify-center space-x-1.5"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Simulate Policy Evaluation</span>
              </button>
            </div>

            {simulationResult && (
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Policy Verdict</span>
                  <span
                    className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                      simulationResult.decision === 'ALLOW'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : simulationResult.decision === 'BLOCK'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}
                  >
                    {simulationResult.decision}
                  </span>
                </div>
                <p className="text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {simulationResult.reason}
                </p>
                <div className="text-[10px] text-slate-400">
                  Approval Required: {simulationResult.requires_approval ? 'YES (Human Gate)' : 'NO'}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
