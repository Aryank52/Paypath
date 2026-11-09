import React, { useState, useEffect } from 'react';
import { X, Search, Sparkles, ArrowRight, ShieldCheck, FileText, CornerDownLeft } from 'lucide-react';
import { useStore } from '../store/useStore';
import { api } from '../services/api';

const QUICK_PROMPTS = [
  'Why is the NovaSound refund eligible under merchant policy?',
  'Find travel wireless noise-cancelling headphones under $100',
  'Show duplicate payment anomalies detected this week',
  'What is the maximum allowed spending limit under Payment Guard?'
];

export const AICommandCenterModal: React.FC = () => {
  const { isCommandCenterOpen, setIsCommandCenterOpen, setActiveTab } = useStore();
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [isThinking, setIsThinking] = useState(false);

  // Keyboard shortcut listener (Cmd/Ctrl + K and Escape)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandCenterOpen(!isCommandCenterOpen);
      }
      if (e.key === 'Escape' && isCommandCenterOpen) {
        setIsCommandCenterOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandCenterOpen, setIsCommandCenterOpen]);

  if (!isCommandCenterOpen) return null;

  const handleExecutePrompt = async (text: string) => {
    setQuery(text);
    setIsThinking(true);
    setResponse(null);

    try {
      const lower = text.toLowerCase();
      if (lower.includes('refund') || lower.includes('eligible') || lower.includes('novasound')) {
        setResponse({
          type: 'RECLAIM_POLICY',
          answer: 'The NovaSound ANC Pro transaction ($89.00) is eligible for a $65.00 partial refund under Nova Electronics Customer Assurance Policy Section 2 ("Damaged Goods & Transit Defects"). Evidence verified cracked plastic headband within the 30-day window.',
          actionLabel: 'Open RECLAIM Resolution Center',
          actionTab: 'reclaim'
        });
      } else if (lower.includes('headphone') || lower.includes('100') || lower.includes('travel')) {
        const commerce = await api.runCommerceWorkflow(text);
        setResponse({
          type: 'COMMERCE',
          answer: `IntentAgent parsed category 'headphones' for 'travel' under $100. ShoppingAgent found the NovaSound ANC Pro ($89.00) compliant with Payment Guard spending policies.`,
          actionLabel: 'View in Shopping Hub',
          actionTab: 'shopping'
        });
      } else if (lower.includes('duplicate')) {
        setResponse({
          type: 'RECOVERY',
          answer: 'Detected potential duplicate billing of $14.99 at MediaNest charged within 5 minutes. Confidence: 95%.',
          actionLabel: 'Review in Recovery Intel',
          actionTab: 'recovery'
        });
      } else {
        setResponse({
          type: 'GENERAL',
          answer: 'Payment Guard enforces a $300.00 single-transaction spending limit, an automatic human approval threshold at $50.00, and blocks gambling/crypto categories.',
          actionLabel: 'Configure in Payment Guard Studio',
          actionTab: 'guard'
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Search Bar Input */}
        <div className="p-4 border-b border-slate-800 flex items-center space-x-3 bg-slate-950">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && query.trim() && handleExecutePrompt(query)}
            placeholder="Ask PayPath AI about transactions, policies, or spending guards..."
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
            autoFocus
          />
          <button
            onClick={() => setIsCommandCenterOpen(false)}
            className="p-1 rounded text-slate-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content & Suggestions */}
        <div className="p-5 space-y-4 max-h-[60vh] overflow-y-auto">
          {!response && !isThinking && (
            <div className="space-y-2">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Suggested Financial Queries
              </div>
              <div className="space-y-1.5">
                {QUICK_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleExecutePrompt(p)}
                    className="w-full text-left p-2.5 rounded-lg bg-slate-950/60 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 flex items-center justify-between group transition-colors"
                  >
                    <span className="group-hover:text-white transition-colors">{p}</span>
                    <CornerDownLeft className="w-3 h-3 text-slate-400 group-hover:text-indigo-400" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {isThinking && (
            <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
              <span>Analyzing transaction intelligence & policies...</span>
            </div>
          )}

          {response && (
            <div className="p-4 rounded-xl bg-slate-950 border border-indigo-500/30 space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold text-indigo-400">
                <Sparkles className="w-4 h-4" />
                <span>PayPath Intelligence Response</span>
              </div>

              <p className="text-xs text-slate-200 leading-relaxed">{response.answer}</p>

              <div className="pt-2 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => {
                    setIsCommandCenterOpen(false);
                    setActiveTab(response.actionTab);
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-indigo-600/20"
                >
                  <span>{response.actionLabel}</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
