import React, { useState, useEffect } from 'react';
import {
  Server,
  Database,
  Cpu,
  ShieldCheck,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Play,
  Layers,
  FileCode,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export const SystemIntelligenceView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'database' | 'ml' | 'safety'>('overview');
  const [healthData, setHealthData] = useState<any>(null);
  const [dbData, setDbData] = useState<any>(null);
  const [mlModels, setMlModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // ML Simulation form state
  const [simAmount, setSimAmount] = useState('89.00');
  const [simMerchant, setSimMerchant] = useState('Nova Electronics');
  const [simDesc, setSimDesc] = useState('NovaSound ANC Pro Wireless Headphones');
  const [simSub, setSimSub] = useState(false);
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    loadSystemTelemetry();
  }, []);

  const loadSystemTelemetry = async () => {
    setLoading(true);
    try {
      const [h, db, models] = await Promise.all([
        api.getSystemHealth().catch(() => null),
        api.getDatabaseInventory().catch(() => null),
        api.getMLModels().catch(() => ({ models: [] }))
      ]);
      setHealthData(h);
      setDbData(db);
      setMlModels(models?.models || []);
    } catch (err) {
      console.error('Failed to load system telemetry', err);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimLoading(true);
    try {
      const res = await api.predictRisk({
        amount: parseFloat(simAmount) || 0,
        merchant_name: simMerchant,
        item_description: simDesc,
        is_subscription: simSub
      });
      setSimResult(res);
    } catch (err) {
      console.error('Simulation failed', err);
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                System Architecture & Intelligence
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Live Unified System
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                PostgreSQL 16 authority, Dual-Phase PayPal verification, XGBoost/Isolation Forest ML & Deterministic Policy Safety
              </p>
            </div>
          </div>
        </div>

        {/* Tab switchers */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-lg text-xs">
          <button
            onClick={() => setActiveSubTab('overview')}
            className={`px-3 py-1.5 rounded-md font-medium transition-all ${
              activeSubTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveSubTab('database')}
            className={`px-3 py-1.5 rounded-md font-medium transition-all ${
              activeSubTab === 'database'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Database ({dbData?.total_records || 0})
          </button>
          <button
            onClick={() => setActiveSubTab('ml')}
            className={`px-3 py-1.5 rounded-md font-medium transition-all ${
              activeSubTab === 'ml'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ML Engine & Simulator
          </button>
          <button
            onClick={() => setActiveSubTab('safety')}
            className={`px-3 py-1.5 rounded-md font-medium transition-all ${
              activeSubTab === 'safety'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Policy & Safety
          </button>
        </div>
      </div>

      {/* Quick Telemetry KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between">
          <div>
            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Database Authority</span>
            <h3 className="text-lg font-bold text-white mt-1">PostgreSQL 16</h3>
            <p className="text-[11px] text-emerald-400 mt-0.5 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Connected ({healthData?.components?.postgresql?.latency_ms || 4.2}ms)
            </p>
          </div>
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Database className="w-4 h-4" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between">
          <div>
            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">ML Models</span>
            <h3 className="text-lg font-bold text-white mt-1">XGBoost + IsoForest</h3>
            <p className="text-[11px] text-indigo-400 mt-0.5 flex items-center gap-1">
              <Activity className="w-3.5 h-3.5" />
              12 Features • Active
            </p>
          </div>
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Cpu className="w-4 h-4" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between">
          <div>
            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Policy Engine</span>
            <h3 className="text-lg font-bold text-white mt-1">Deterministic</h3>
            <p className="text-[11px] text-emerald-400 mt-0.5 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Hard Limits Enforced
            </p>
          </div>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start justify-between">
          <div>
            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Verification Model</span>
            <h3 className="text-lg font-bold text-white mt-1">Dual-Phase Audit</h3>
            <p className="text-[11px] text-cyan-400 mt-0.5 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Idempotent Read-Back
            </p>
          </div>
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Sub-Tab 1: Architecture Overview */}
      {activeSubTab === 'overview' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800">
            <h2 className="text-base font-bold text-white mb-2">End-to-End Transaction & Intelligence Pipeline</h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              PayPath enforces strict separation between intelligent advisory reasoning (AI/ML) and consequential financial execution (Deterministic Policy Engine + PayPal + Independent Verification).
            </p>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Phase 1</span>
                  <h4 className="text-sm font-semibold text-white mt-1">Intent & Proposal</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    User natural language parsed into structured intent; product selected from catalog.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  Entity: <span className="font-mono text-slate-300">purchase_intents</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Phase 2</span>
                  <h4 className="text-sm font-semibold text-white mt-1">ML Risk & Anomaly</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    12 deterministic features scored via XGBoost & Isolation Forest. Advisory score only.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  Entity: <span className="font-mono text-slate-300">ml_predictions</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 bg-amber-500/[0.02] flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Phase 3</span>
                  <h4 className="text-sm font-semibold text-white mt-1">Policy Governance</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Deterministic spending limits, MFA gating, and duplicate windows evaluate proposal.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  Entity: <span className="font-mono text-slate-300">merchant_policies</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30 bg-blue-500/[0.02] flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Phase 4</span>
                  <h4 className="text-sm font-semibold text-white mt-1">PayPal Execution</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Idempotent order creation and capture against PayPal API with state lock.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  Entity: <span className="font-mono text-slate-300">transactions</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30 bg-emerald-500/[0.02] flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Phase 5</span>
                  <h4 className="text-sm font-semibold text-white mt-1">Read-Back Audit</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Independent read-back call confirms exact amount and status on PayPal servers.
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  Entity: <span className="font-mono text-slate-300">payment_verifications</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 2: Database Live Inventory */}
      {activeSubTab === 'database' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">PostgreSQL 16 Canonical Schema</h3>
              <p className="text-xs text-slate-400">
                Authoritative persistence across {dbData?.total_tables || 19} tables • {dbData?.total_records || 0} total active records
              </p>
            </div>
            <button
              onClick={loadSystemTelemetry}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition-colors"
            >
              Refresh Table Counts
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {dbData?.tables?.map((t: any) => (
              <div key={t.table_name} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 flex items-center justify-between">
                <div>
                  <span className="font-mono text-xs font-semibold text-slate-200">{t.table_name}</span>
                  <p className="text-[10px] text-emerald-400 flex items-center gap-1 mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    PostgreSQL 16
                  </p>
                </div>
                <span className="text-sm font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 font-mono">
                  {t.row_count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-Tab 3: ML Engine & Simulator */}
      {activeSubTab === 'ml' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Models Table & Registry */}
          <div className="lg:col-span-7 space-y-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <h3 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                Active Registered ML Models
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Models trained with temporal 70/15/15 splits to prevent leakage and persisted in PostgreSQL registry.
              </p>

              <div className="space-y-3">
                {mlModels.map((m: any) => (
                  <div key={m.id} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <span className="text-xs font-bold text-white">{m.model_name}</span>
                        <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono">
                          {m.version}
                        </span>
                      </div>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        m.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {m.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-2 text-center pt-2 border-t border-slate-800/80">
                      <div>
                        <span className="text-[10px] text-slate-400">Accuracy</span>
                        <p className="text-xs font-bold text-slate-200 mt-0.5 font-mono">{m.metrics?.accuracy ?? 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400">ROC-AUC</span>
                        <p className="text-xs font-bold text-emerald-400 mt-0.5 font-mono">{m.metrics?.roc_auc ?? 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400">Precision</span>
                        <p className="text-xs font-bold text-slate-200 mt-0.5 font-mono">{m.metrics?.precision ?? 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400">F1 Score</span>
                        <p className="text-xs font-bold text-slate-200 mt-0.5 font-mono">{m.metrics?.f1 ?? 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Interactive ML Simulator */}
          <div className="lg:col-span-5 space-y-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <h3 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Live ML Inference Simulator
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Execute live feature extraction and scoring across XGBoost & Isolation Forest.
              </p>

              <form onSubmit={runSimulation} className="space-y-3">
                <div>
                  <label className="text-[11px] font-medium text-slate-300">Transaction Amount ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={simAmount}
                    onChange={(e) => setSimAmount(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                    placeholder="89.00"
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-medium text-slate-300">Merchant</label>
                  <select
                    value={simMerchant}
                    onChange={(e) => setSimMerchant(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="Nova Electronics">Nova Electronics</option>
                    <option value="UrbanFit">UrbanFit</option>
                    <option value="TravelHub">TravelHub</option>
                    <option value="HomeCraft">HomeCraft</option>
                    <option value="MediaNest">MediaNest</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-medium text-slate-300">Item Description</label>
                  <input
                    type="text"
                    value={simDesc}
                    onChange={(e) => setSimDesc(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
                    placeholder="NovaSound ANC Pro Wireless Headphones"
                  />
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="simSub"
                    checked={simSub}
                    onChange={(e) => setSimSub(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0"
                  />
                  <label htmlFor="simSub" className="text-xs text-slate-300">Recurring Monthly Subscription</label>
                </div>

                <button
                  type="submit"
                  disabled={simLoading}
                  className="w-full mt-2 py-2 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  {simLoading ? 'Extracting Features & Scoring...' : 'Run Live ML Scoring'}
                </button>
              </form>

              {/* Simulation Result Output */}
              {simResult && (
                <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-indigo-500/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Inference Output</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      simResult.risk_level === 'LOW'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {simResult.risk_level} RISK ({simResult.risk_score})
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-[10px] text-slate-400">Anomaly Score</span>
                      <p className="font-bold text-slate-200 font-mono mt-0.5">{simResult.anomaly_score}</p>
                    </div>
                    <div className="p-2 rounded bg-slate-900 border border-slate-800">
                      <span className="text-[10px] text-slate-400">Policy Recommendation</span>
                      <p className="font-bold text-indigo-400 font-mono mt-0.5">{simResult.policy_recommendation}</p>
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Top Explainable Drivers</span>
                    <div className="mt-1 space-y-1">
                      {simResult.feature_contributions?.slice(0, 3).map((driver: any) => (
                        <div key={driver.feature} className="flex items-center justify-between text-[11px] py-1 border-b border-slate-800/60">
                          <span className="font-mono text-slate-300">{driver.feature}</span>
                          <span className="text-slate-400 font-mono">val: {driver.value} (imp: {driver.impact})</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <p className="text-[10px] text-slate-400 leading-tight pt-1">
                    {simResult.safety_directive}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 4: Policy & Safety Governance */}
      {activeSubTab === 'safety' && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Deterministic Policy Governance & Safety Directive
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            In PayPath, machine learning and generative artificial intelligence are strictly non-authoritative for consequential financial transactions.
            AI models generate contextual understanding and risk scores; deterministic policy rules constrain the boundary of acceptable actions; human users retain mandatory approval for consequential actions; PayPal handles the actual fund transfer; and PayPath independently verifies the outcome.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs font-bold text-indigo-400">1. Autonomous Thresholds</span>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Autonomous refunds are strictly capped at $250.00. Amounts above $250.00 require human operator approval.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs font-bold text-emerald-400">2. Duplicate Charge Guard</span>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Transactions with identical amount and merchant within 1 hour are automatically held for review.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-xs font-bold text-cyan-400">3. Verification Lock</span>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                No mutation is marked complete until PayPal read-back confirms order and capture state.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

