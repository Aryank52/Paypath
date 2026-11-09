import React, { useEffect, useState } from 'react';
import { Store, FileText, CheckCircle2, Sliders, Play, Upload, ShieldCheck, Sparkles } from 'lucide-react';
import { api } from '../services/api';

export const MerchantPortal: React.FC = () => {
  const [merchants, setMerchants] = useState<any[]>([]);
  const [selectedMerchant, setSelectedMerchant] = useState<any>(null);
  const [policyTitle, setPolicyTitle] = useState('Holiday 45-Day Customer Assurance & Transit Warranty');
  const [policyContent, setPolicyContent] = useState(
    '# Holiday Transit Policy\n\n## 1. Transit Damage Coverage\nItems damaged during holiday shipping qualify for a 75% partial reimbursement or immediate replacement if reported within 45 days.\n\n## 2. Evidence Requirements\nPhotographic verification of package condition is required.'
  );
  const [simulationAmount, setSimulationAmount] = useState(120.0);
  const [simulationAge, setSimulationAge] = useState(18);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetch('/api/v1/merchants')
      .then((res) => res.json())
      .then((data) => {
        setMerchants(data);
        if (data.length > 0) setSelectedMerchant(data[0]);
      })
      .catch(console.error);
  }, []);

  const handleUploadPolicy = async () => {
    if (!selectedMerchant) return;
    setIsUploading(true);
    try {
      const res = await fetch(`/api/v1/merchants/${selectedMerchant.id}/policies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: policyTitle,
          policy_type: 'REFUND',
          content: policyContent,
          rules: { return_window_days: 45, partial_refund_max_pct: 75 }
        })
      });
      const data = await res.json();
      alert(`Policy ingested as ${data.status}! Chunks indexed: ${data.chunks_indexed}`);
    } catch (err) {
      console.error(err);
      alert('Error uploading policy');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSimulate = async () => {
    if (!selectedMerchant) return;
    setIsSimulating(true);
    try {
      const res = await fetch(`/api/v1/merchants/${selectedMerchant.id}/simulate-policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_amount: simulationAmount,
          issue_type: 'DAMAGED_ITEM',
          transaction_age_days: simulationAge,
          evidence_provided: true
        })
      });
      const data = await res.json();
      setSimulationResult(data);
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
          <span>Multi-Merchant Portal & Policy Studio</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Tenant Isolated
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage merchant return rules, ingest documents with RAG chunking, and simulate dispute outcomes before publishing.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Column: Merchant Selection & Policy Ingestion */}
        <div className="md:col-span-6 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Store className="w-3.5 h-3.5 text-indigo-400" />
              <span>Select Merchant Tenant</span>
            </h2>

            <div className="grid grid-cols-2 gap-2">
              {merchants.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setSelectedMerchant(m)}
                  className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                    selectedMerchant?.id === m.id
                      ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-semibold text-white">{m.name}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5 font-mono">{m.slug}</div>
                </button>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-800 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                <Upload className="w-3.5 h-3.5 text-emerald-400" />
                <span>Ingest & Chunk Return Policy</span>
              </h3>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Policy Title</label>
                <input
                  type="text"
                  value={policyTitle}
                  onChange={(e) => setPolicyTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Markdown Policy Content</label>
                <textarea
                  value={policyContent}
                  onChange={(e) => setPolicyContent(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono text-[11px] resize-none"
                />
              </div>

              <button
                onClick={handleUploadPolicy}
                disabled={isUploading}
                className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center space-x-1.5"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>{isUploading ? 'Chunking & Indexing...' : 'Ingest & Index Policy (Draft)'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Policy Simulation Workbench */}
        <div className="md:col-span-6 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Play className="w-3.5 h-3.5 text-emerald-400" />
              <span>Policy Simulation Workbench</span>
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Test how this merchant's return rules evaluate simulated customer claims (<strong className="text-white">Transaction + Evidence + Policy = Predicted Outcome</strong>).
            </p>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Simulated Transaction Amount ($)</label>
                <input
                  type="number"
                  value={simulationAmount}
                  onChange={(e) => setSimulationAmount(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Days Elapsed Since Delivery</label>
                <input
                  type="number"
                  value={simulationAge}
                  onChange={(e) => setSimulationAge(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                onClick={handleSimulate}
                disabled={isSimulating}
                className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/30 transition-all flex items-center justify-center space-x-1.5"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Run Policy Simulation</span>
              </button>
            </div>

            {simulationResult && (
              <div className="pt-3 border-t border-slate-800 space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Predicted Verdict</span>
                  <span
                    className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                      simulationResult.predicted_outcome.decision === 'ALLOW'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}
                  >
                    {simulationResult.predicted_outcome.decision}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                  <div className="text-slate-300">{simulationResult.predicted_outcome.reason}</div>
                  <div className="text-[11px] text-emerald-400 font-semibold">
                    Simulated Refund: ${simulationResult.simulated_input.proposed_refund.toFixed(2)} USD
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Human Gate: {simulationResult.predicted_outcome.requires_human_approval ? 'REQUIRED' : 'AUTO_ALLOWED'}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
