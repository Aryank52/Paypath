import React, { useState } from 'react';
import {
  RotateCcw,
  Upload,
  CheckCircle2,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  FileText,
  Sparkles,
  Camera,
  Check,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { useStore } from '../store/useStore';

export const ReclaimResolutionCenter: React.FC = () => {
  const { setActiveTab } = useStore();
  const [step, setStep] = useState<'upload' | 'evaluating' | 'proposal' | 'executing' | 'resolved'>('upload');
  const [issueType, setIssueType] = useState('DAMAGED_ITEM');
  const [description, setDescription] = useState('My headphones arrived with a cracked plastic headband on the left ear cup.');
  const [evidenceName, setEvidenceName] = useState('nova_damaged_headband.jpg');
  const [resolutionData, setResolutionData] = useState<any>(null);
  const [refundResult, setRefundResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // 1. Submit Evidence & Run RECLAIM Workflow
  const handleAnalyzeDispute = async () => {
    setIsProcessing(true);
    setStep('evaluating');

    try {
      // Run full multi-agent RECLAIM pipeline
      const workflow = await api.runReclaimWorkflow({
        transaction_amount: 89.00,
        merchant_name: 'Nova Electronics',
        issue_type: issueType,
        user_description: description,
        evidence_file_name: evidenceName,
        transaction_age_days: 14
      });

      setResolutionData(workflow);
      setStep('proposal');
    } catch (err) {
      console.error(err);
      alert('Error analyzing dispute. Please try again.');
      setStep('upload');
    } finally {
      setIsProcessing(false);
    }
  };

  // 2. Human Approves & PayPal Executes Refund Mutation
  const handleApproveRefund = async () => {
    setIsProcessing(true);
    setStep('executing');

    try {
      // Call PayCore to execute refund on sandbox and perform independent read-back verification
      const refund = await api.refundPayment({
        transaction_id: 'tx_nova_anc_hero',
        amount: resolutionData?.resolution?.recommended_amount || 65.00,
        reason: 'Customer reported damaged item approved via RECLAIM Engine'
      });

      setRefundResult(refund);
      setStep('resolved');
    } catch (err) {
      console.error(err);
      alert('Error executing refund mutation. Please try again.');
      setStep('proposal');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">RECLAIM Post-Purchase Resolution Hub</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Hero Demo Flow
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Multimodal evidence inspection, RAG policy grounding, deterministic guardrails, and PayPal-verified refund actions.
          </p>
        </div>

        {/* Workflow State Tracker */}
        <div className="flex items-center space-x-2">
          {['1. Evidence', '2. Policy RAG', '3. Approval', '4. PayPal Verified'].map((label, idx) => (
            <div
              key={label}
              className={`text-[10px] font-semibold px-2 py-1 rounded-md border ${
                (step === 'upload' && idx === 0) ||
                (step === 'evaluating' && idx <= 1) ||
                (step === 'proposal' && idx <= 2) ||
                (step === 'resolved' && idx <= 3)
                  ? 'bg-indigo-600/20 text-indigo-400 border-indigo-500/30'
                  : 'bg-slate-900 text-slate-500 border-slate-800'
              }`}
            >
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Main Two-Column Interactive Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Dispute & Evidence Uploader */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Camera className="w-3.5 h-3.5 text-indigo-400" />
              <span>Purchase & Evidence Intake</span>
            </h2>

            {/* Target Transaction Pill */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-200">Nova Electronics</div>
                <div className="text-[11px] text-slate-400">NovaSound ANC Pro Headphones</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-bold text-white">$89.00 USD</div>
                <div className="text-[10px] text-emerald-400 font-medium">Captured 14 days ago</div>
              </div>
            </div>

            {/* Issue Selector */}
            <div>
              <label className="text-[11px] font-medium text-slate-300 block mb-1.5">Reported Issue</label>
              <select
                value={issueType}
                onChange={(e) => setIssueType(e.target.value)}
                disabled={step !== 'upload'}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-60"
              >
                <option value="DAMAGED_ITEM">Damaged or Defective Item (Transit Damage)</option>
                <option value="WRONG_ITEM">Incorrect Item Received</option>
                <option value="NOT_RECEIVED">Item Never Received</option>
                <option value="DUPLICATE_CHARGE">Suspected Duplicate Billing</option>
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="text-[11px] font-medium text-slate-300 block mb-1.5">Issue Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={step !== 'upload'}
                rows={3}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-60 resize-none"
              />
            </div>

            {/* Photo Evidence Uploader */}
            <div>
              <label className="text-[11px] font-medium text-slate-300 block mb-1.5">
                Photographic Evidence (Required by Merchant Policy)
              </label>
              <div className="p-4 rounded-lg border-2 border-dashed border-slate-800 hover:border-indigo-500/50 bg-slate-950/40 text-center transition-colors">
                <Upload className="w-5 h-5 text-indigo-400 mx-auto mb-1.5" />
                <div className="text-xs font-medium text-slate-300">{evidenceName}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">JPEG / PNG • 2.4 MB</div>
              </div>
            </div>

            {/* Submit Action */}
            {step === 'upload' && (
              <button
                onClick={handleAnalyzeDispute}
                disabled={isProcessing}
                className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Run RECLAIM Intelligence</span>
              </button>
            )}
          </div>
        </div>

        {/* Right Column: AI Analysis, Policy Grounding & PayPal Action */}
        <div className="lg:col-span-7 space-y-4">
          {step === 'upload' && (
            <div className="p-8 rounded-xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mx-auto">
                <RotateCcw className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-semibold text-white">RECLAIM Post-Purchase Engine Ready</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                When you click "Run RECLAIM Intelligence", PayPath will coordinate the Evidence Agent to classify the damage,
                query the merchant's indexed refund policy via RAG, and formulate a policy-bounded resolution proposal.
              </p>
            </div>
          )}

          {step === 'evaluating' && (
            <div className="p-8 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-3">
              <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin mx-auto" />
              <h3 className="text-sm font-semibold text-white">Coordinating Agentic RAG Pipeline...</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Evidence Agent inspecting damage • Policy Agent retrieving Nova Electronics refund policy • Risk Agent evaluating boundaries.
              </p>
            </div>
          )}

          {(step === 'proposal' || step === 'executing' || step === 'resolved') && resolutionData && (
            <div className="space-y-4">
              {/* Evidence Agent Inspection Result */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-bold text-white">Evidence Agent Assessment</span>
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Confidence: 94%
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {resolutionData.evidence?.analysis_summary}
                </p>
              </div>

              {/* RAG Policy Citation Card */}
              <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs font-bold text-indigo-300">
                      RAG Policy Evidence ({resolutionData.policy?.merchant_name})
                    </span>
                  </div>
                  <span className="text-[10px] text-indigo-400 font-medium">
                    {resolutionData.policy?.applicability}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/80 border border-indigo-950 text-xs text-slate-300 italic leading-relaxed">
                  "{resolutionData.policy?.excerpt}"
                </div>
                <div className="text-[10px] text-slate-400">
                  Document: {resolutionData.policy?.policy_title} • Section: {resolutionData.policy?.section}
                </div>
              </div>

              {/* Resolution Proposal & Human Approval Box */}
              <div className="p-5 rounded-xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-700 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Recommended Resolution</div>
                    <div className="text-2xl font-bold text-emerald-400 mt-0.5">
                      ${resolutionData.resolution?.recommended_amount?.toFixed(2)}{' '}
                      <span className="text-xs font-semibold text-slate-300 uppercase">
                        {resolutionData.resolution?.proposed_resolution?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      Human Approval Required
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {resolutionData.resolution?.ai_reasoning}
                </p>

                {/* State: Pending Approval */}
                {step === 'proposal' && (
                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                    <div className="text-[11px] text-slate-400">
                      Authorizing will execute a PayPal Sandbox refund and independently audit settlement.
                    </div>
                    <button
                      onClick={handleApproveRefund}
                      disabled={isProcessing}
                      className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition-all flex items-center space-x-2"
                    >
                      <Check className="w-4 h-4" />
                      <span>Approve ${resolutionData.resolution?.recommended_amount?.toFixed(2)} Refund</span>
                    </button>
                  </div>
                )}

                {/* State: Executing */}
                {step === 'executing' && (
                  <div className="p-4 rounded-lg bg-slate-950 text-center space-y-2">
                    <RefreshCw className="w-5 h-5 text-emerald-400 animate-spin mx-auto" />
                    <div className="text-xs font-semibold text-white">Dispatching to PayPal Sandbox...</div>
                    <div className="text-[10px] text-slate-400">
                      Executing refund mutation & performing secondary read-back verification.
                    </div>
                  </div>
                )}

                {/* State: Resolved & Verified */}
                {step === 'resolved' && refundResult && (
                  <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 space-y-3">
                    <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                      <ShieldCheck className="w-5 h-5" />
                      <span>Case Resolved & Verified by PayPal</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                      <div>
                        PayPal Refund ID:{' '}
                        <span className="font-mono text-emerald-300">{refundResult.refund_id}</span>
                      </div>
                      <div>
                        Amount Refunded:{' '}
                        <span className="font-bold text-white">${refundResult.amount?.toFixed(2)} USD</span>
                      </div>
                      <div>
                        Audit Verification:{' '}
                        <span className="text-emerald-400 font-semibold">{refundResult.verification_status}</span>
                      </div>
                      <div>
                        Idempotency Check:{' '}
                        <span className="text-slate-400">Enforced & Recorded</span>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-emerald-900/50 flex justify-end">
                      <button
                        onClick={() => setActiveTab('transactions')}
                        className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs border border-slate-700 transition-colors flex items-center space-x-1.5"
                      >
                        <span>View in Transaction Explorer</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
