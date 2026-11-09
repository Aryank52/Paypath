import React, { useState } from 'react';
import { Cpu, CheckCircle2, Play, Sparkles, ShieldCheck, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { AgentTraceStep } from '../types';

export const AgentTraceVisualizer: React.FC = () => {
  const [traceSteps, setTraceSteps] = useState<AgentTraceStep[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [activeWorkflow, setActiveWorkflow] = useState<string | null>(null);

  const runReclaimTrace = async () => {
    setIsRunning(true);
    setActiveWorkflow('RECLAIM Workflow');
    try {
      const res = await api.runReclaimWorkflow({
        transaction_amount: 89.0,
        merchant_name: 'Nova Electronics',
        issue_type: 'DAMAGED_ITEM',
        user_description: 'Headphones arrived with cracked plastic headband.',
        evidence_file_name: 'cracked_headband.jpg',
        transaction_age_days: 14
      });
      setTraceSteps(res.trace || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  const runCommerceTrace = async () => {
    setIsRunning(true);
    setActiveWorkflow('Agentic Commerce Workflow');
    try {
      const res = await api.runCommerceWorkflow('Find wireless noise-cancelling headphones under $100 for travel');
      setTraceSteps(res.trace || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Multi-Agent Execution Visualizer</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Typed Message Bus
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Observe specialized agents coordinating over validated Pydantic message schemas with deterministic policy enforcement.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={runCommerceTrace}
            disabled={isRunning}
            className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center space-x-1.5"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Run Commerce Trace</span>
          </button>
          <button
            onClick={runReclaimTrace}
            disabled={isRunning}
            className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/30 transition-all flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Run RECLAIM Trace</span>
          </button>
        </div>
      </div>

      {isRunning ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-slate-900/40 rounded-xl border border-slate-800">
          Agents coordinating over typed bus...
        </div>
      ) : traceSteps.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-slate-900/40 rounded-xl border border-slate-800">
          Click either button above to trigger live agent coordination traces.
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs font-semibold text-indigo-400 flex items-center space-x-1.5 px-1">
            <Cpu className="w-3.5 h-3.5" />
            <span>Active Trace: {activeWorkflow} ({traceSteps.length} Steps)</span>
          </div>

          <div className="space-y-2.5">
            {traceSteps.map((step, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-[10px]">
                      {idx + 1}
                    </span>
                    <span className="text-xs font-bold text-white">{step.agent_name}</span>
                    <span className="text-[10px] text-slate-400">({step.role})</span>
                  </div>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {step.status}
                  </span>
                </div>

                <div className="text-xs text-slate-300 font-mono text-[11px] bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  {step.summary}
                </div>

                <div className="text-[10px] text-slate-400 flex justify-between">
                  <span>Action: {step.action}</span>
                  <span>{new Date(step.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
