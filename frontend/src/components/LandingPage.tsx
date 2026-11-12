import React from 'react';
import { 
  ShieldCheck, 
  ArrowRight, 
  Brain, 
  CheckCircle2, 
  FileCheck2, 
  Cpu, 
  TrendingUp, 
  RefreshCw, 
  Sparkles,
  Lock,
  Building2,
  ChevronRight,
  Eye,
  SlidersHorizontal,
  Bot
} from 'lucide-react';
import { useStore } from '../store/useStore';

import { api } from '../services/api';

export const LandingPage: React.FC = () => {
  const { setAuthModal, setActiveTab, loginUser } = useStore();

  const handleLaunchDemo = (role: 'SHOPPER' | 'PLATFORM_ADMIN') => {
    const token = localStorage.getItem('paypath_token');
    if (token) {
      if (role === 'PLATFORM_ADMIN') {
        setActiveTab('system');
      } else {
        setActiveTab('overview');
      }
    } else {
      setAuthModal('login');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full">
        <div className="absolute inset-0 bg-radial-gradient pointer-events-none opacity-40"></div>
        
        {/* Trust Pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-8">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>FINTECH INTELLIGENCE & POLICY-AWARE PAYMENT ACTION</span>
        </div>

        {/* Primary H1 */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white max-w-4xl leading-[1.12]">
          Your payments should <span className="bg-gradient-to-r from-indigo-400 via-sky-300 to-indigo-200 bg-clip-text text-transparent">understand you.</span>
        </h1>

        {/* Supporting Copy */}
        <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-2xl leading-relaxed">
          PayPath combines AI transaction intelligence, policy-aware agents, and PayPal-powered execution to help you understand, control, and resolve transactions securely.
        </p>

        {/* Hero CTAs */}
        <div className="mt-10 flex flex-wrap items-center gap-4">
          <button
            onClick={() => setAuthModal('signup')}
            className="px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
          >
            <span>Get Started Free</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <a
            href="#how-it-works"
            className="px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white font-medium text-sm transition-all"
          >
            See How It Works
          </a>
        </div>

        {/* Instant Exploration Cards */}
        <div className="mt-12 pt-8 border-t border-slate-900/80 flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">Instant Live Portal:</span>
          <button
            onClick={() => handleLaunchDemo('SHOPPER')}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-indigo-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Bot className="w-3.5 h-3.5 text-indigo-400" />
            <span>Shopper Portal (Alex Chen)</span>
          </button>
          <button
            onClick={() => handleLaunchDemo('PLATFORM_ADMIN')}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-sky-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-sky-400" />
            <span>Control Center (Marcus Vance)</span>
          </button>
        </div>
      </section>

      {/* How It Works: Understand. Decide. Act. Verify. */}
      <section id="how-it-works" className="py-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full border-t border-slate-900">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-xs font-semibold tracking-widest uppercase text-indigo-400">Core Architecture</h2>
          <p className="mt-2 text-3xl font-bold text-white">Understand. Decide. Act. Verify.</p>
          <p className="mt-3 text-slate-400 text-sm">
            Four disciplined operational phases transform ambiguous charges into deterministic, verified resolutions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Phase 1: Understand */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 relative group hover:border-indigo-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm mb-4">
              01
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Understand</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              PayPath ingests transaction context, item descriptions, user budget constraints, and uploaded evidence to build a semantic profile.
            </p>
          </div>

          {/* Phase 2: Decide */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 relative group hover:border-indigo-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-sm mb-4">
              02
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Decide</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              RAG policy extraction, XGBoost risk evaluation, and deterministic policy rules evaluate eligibility with clear mathematical bounds.
            </p>
          </div>

          {/* Phase 3: Act */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 relative group hover:border-indigo-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm mb-4">
              03
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Act</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Authorized actions (checkout orders, partial refunds, dispute filings) are dispatched with strict idempotency via PayCore and PayPal.
            </p>
          </div>

          {/* Phase 4: Verify */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 relative group hover:border-indigo-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-sm mb-4">
              04
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Verify</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              PayPath performs independent read-backs against PayPal and PostgreSQL to confirm funds moved accurately before marking transactions verified.
            </p>
          </div>
        </div>
      </section>

      {/* Transaction Intelligence Bento Grid */}
      <section className="py-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full border-t border-slate-900">
        <div className="max-w-2xl mb-14">
          <h2 className="text-xs font-semibold tracking-widest uppercase text-indigo-400">Intelligent Platform</h2>
          <p className="mt-2 text-3xl font-bold text-white">Full-Stack Intelligence Hierarchy</p>
          <p className="mt-3 text-slate-400 text-sm">
            Built for transparency, verifiable accountability, and zero unauthorized financial mutations.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Payment Guard (Large) */}
          <div className="md:col-span-2 bg-gradient-to-br from-slate-900/90 to-slate-900/40 border border-slate-800 rounded-3xl p-8 relative overflow-hidden">
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
                Deterministic Policy Override
              </span>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Payment Guard Pre-Transaction Firewall</h3>
            <p className="text-slate-400 text-sm max-w-lg mb-6 leading-relaxed">
              Every checkout intent is pre-evaluated against user spend caps, category restrictions, and merchant return policies before a single dollar moves.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-500 block">Decision</span>
                <span className="text-emerald-400 font-semibold mt-1 block">ALLOW</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-500 block">Review</span>
                <span className="text-amber-400 font-semibold mt-1 block">REVIEW</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-500 block">Enforcement</span>
                <span className="text-rose-400 font-semibold mt-1 block">BLOCK</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-slate-500 block">Governance</span>
                <span className="text-indigo-400 font-semibold mt-1 block">ESCALATE</span>
              </div>
            </div>
          </div>

          {/* Card 2: RECLAIM */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mb-6">
                <RefreshCw className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">RECLAIM Resolution</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-4">
                Guided dispute and refund recovery workspace. Evaluates damaged items, late shipments, and duplicate charges against exact policy clauses.
              </p>
            </div>
            <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400 flex items-center justify-between">
              <span>Automated Refund SLA</span>
              <span className="font-semibold text-sky-400">&lt; 3 minutes</span>
            </div>
          </div>

          {/* Card 3: Multi-Agent Consensus */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-6">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">7 Specialized Micro-Agents</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Intent, Shopping, Guard, Evidence, Risk, Resolution, and Verification agents collaborate with tool logging and state persistence.
              </p>
            </div>
            <div className="mt-6 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-purple-300 font-mono">
              Agent Consensus: 100% Agreement
            </div>
          </div>

          {/* Card 4: Machine Learning (Large) */}
          <div className="md:col-span-2 bg-gradient-to-br from-slate-900/90 to-slate-900/40 border border-slate-800 rounded-3xl p-8 relative overflow-hidden">
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <TrendingUp className="w-6 h-6" />
              </div>
              <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono">
                XGBoost + Isolation Forest v1.0.0
              </span>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Leakage-Free Advisory Machine Learning</h3>
            <p className="text-slate-400 text-sm max-w-xl leading-relaxed mb-6">
              12 behavioral features trained on temporal 70/15/15 splits provide transparent risk scoring. ML operates as an advisory signal—never holding unilateral execution authority.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Zero Data Leakage</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Advisory Risk Signals</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Isolation Forest Anomaly Detection</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Central Trust Model */}
      <section className="py-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full border-t border-slate-900">
        <div className="bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-950 border border-indigo-500/20 rounded-3xl p-8 sm:p-12 text-center max-w-4xl mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto mb-6">
            <Lock className="w-6 h-6" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">The PayPath Trust Contract</h2>
          <p className="text-slate-300 text-base max-w-xl mx-auto mb-8 leading-relaxed">
            Financial safety requires clear boundaries. We never delegate absolute authority to stochastic AI models.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-sm">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">01</span>
              <span className="font-semibold text-white">AI recommends</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">02</span>
              <span className="font-semibold text-indigo-300">Policies constrain</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">03</span>
              <span className="font-semibold text-sky-300">Humans approve</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">04</span>
              <span className="font-semibold text-emerald-300">PayPal executes</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">05</span>
              <span className="font-semibold text-purple-300">PayPath verifies</span>
            </div>
          </div>
        </div>
      </section>

      {/* Merchant Capabilities */}
      <section className="py-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full border-t border-slate-900">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium mb-4">
              <Building2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>For Modern Merchants</span>
            </div>
            <h2 className="text-3xl font-bold text-white leading-tight">
              Transform Return Policies Into Automated, Deterministic Resolution
            </h2>
            <p className="mt-4 text-slate-400 text-sm leading-relaxed">
              Upload natural language policies. PayPath indexes them into vector chunks and runs interactive policy simulations so your support team resolves claims consistently in seconds.
            </p>
            <ul className="mt-6 space-y-3 text-sm text-slate-300">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>Automatic clause retrieval with pgvector</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>Interactive policy simulator for edge cases</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>Scoped tenant isolation across merchants</span>
              </li>
            </ul>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 font-mono text-xs text-slate-300 space-y-3">
            <div className="text-slate-500">// Merchant Policy Simulation</div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
              <span className="text-indigo-400 font-semibold">POLICY:</span> Nova Electronics 30-Day Defective Gear
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
              <span className="text-amber-400 font-semibold">SCENARIO:</span> Damaged ANC Pro Headphones ($89.00)
            </div>
            <div className="p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-lg text-emerald-300">
              <span className="font-semibold">RESOLUTION:</span> Full Refund Approved | Policy Section 3.2
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-20 px-6 sm:px-12 lg:px-20 max-w-7xl mx-auto w-full border-t border-slate-900 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
          Experience Intelligent Payment Protection
        </h2>
        <p className="text-slate-400 text-sm max-w-lg mx-auto mb-8">
          Join shoppers, merchants, and finance teams who rely on PayPath to understand, decide, act, and verify every transaction.
        </p>
        <button
          onClick={() => setAuthModal('signup')}
          className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm inline-flex items-center gap-2 shadow-xl shadow-indigo-600/20 transition-all cursor-pointer"
        >
          <span>Create Free Account</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </section>
    </div>
  );
};
