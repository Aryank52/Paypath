import React, { useState } from 'react';
import {
  Search,
  Sparkles,
  ShoppingBag,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
  CreditCard
} from 'lucide-react';
import { api } from '../services/api';
import { Product, GuardEvaluation } from '../types';
import { useStore } from '../store/useStore';

export const ShoppingCenter: React.FC = () => {
  const { setActiveTab } = useStore();
  const [prompt, setPrompt] = useState('Find me wireless noise-cancelling headphones under $100 for travel.');
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [guardResult, setGuardResult] = useState<GuardEvaluation | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState<any>(null);

  const handleSearchWithIntent = async () => {
    setIsSearching(true);
    setPurchaseSuccess(null);
    try {
      // 1. Run multi-agent commerce workflow (Intent -> Shopping -> Guard)
      const res = await api.runCommerceWorkflow(prompt);
      setProducts(res.products || []);
      if (res.selected_product) {
        setSelectedProduct(res.selected_product);
        setGuardResult(res.guard);
      }
    } catch (err) {
      console.error(err);
      alert('Error searching products.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectProduct = async (product: Product) => {
    setSelectedProduct(product);
    try {
      const guard = await api.evaluateGuard({
        amount: product.price,
        merchant_name: product.merchant_name,
        category: product.category
      });
      setGuardResult(guard);
    } catch (err) {
      console.error(err);
    }
  };

  const handleExecuteGuardedPurchase = async () => {
    if (!selectedProduct) return;
    setIsExecuting(true);
    try {
      // 1. Create PayPal Order via PayCore
      const order = await api.createOrder({
        amount: selectedProduct.price,
        currency: selectedProduct.currency,
        merchant_name: selectedProduct.merchant_name,
        item_description: selectedProduct.title
      });

      // 2. Authorize & Capture Order via PayCore (with independent verification)
      const capture = await api.captureOrder(order.order_id);
      setPurchaseSuccess(capture);
    } catch (err) {
      console.error(err);
      alert('Failed to execute purchase.');
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Title */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl font-bold text-white tracking-tight">Agentic Commerce & Intent Hub</h1>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Channel3 Normalized Feed
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Express purchase goals in natural language. PayPath extracts intent constraints, searches verified products, and enforces Payment Guard authorization before any money moves.
        </p>
      </div>

      {/* Natural Language Intent Input */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
        <label className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>User Intent Prompt</span>
        </label>
        <div className="flex items-center space-x-2.5">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Find travel headphones under $100. Do not purchase without approval."
            className="flex-1 px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            onClick={handleSearchWithIntent}
            disabled={isSearching}
            className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center space-x-1.5 whitespace-nowrap"
          >
            <Search className="w-3.5 h-3.5" />
            <span>{isSearching ? 'Analyzing Intent...' : 'Search with Guard'}</span>
          </button>
        </div>
      </div>

      {/* Results Layout */}
      {products.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Products Column */}
          <div className="md:col-span-7 space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">Recommended Products</h2>
            <div className="space-y-3">
              {products.map((p) => {
                const isSelected = selectedProduct?.id === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => handleSelectProduct(p)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/10'
                        : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-xs font-bold text-white">{p.title}</div>
                        <div className="text-[11px] text-indigo-400 font-medium mt-0.5">{p.merchant_name}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-white">${p.price.toFixed(2)}</div>
                        <div className="text-[10px] text-slate-400">{p.currency}</div>
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 mt-2 line-clamp-2">
                      {p.recommendation_rationale}
                    </p>

                    <div className="mt-3 flex items-center justify-between text-[11px]">
                      <div className="flex items-center space-x-2 text-slate-400">
                        <span>Rating: {p.rating} / 5.0</span>
                        <span>•</span>
                        <span className="text-emerald-400">In Stock</span>
                      </div>
                      {p.matches_budget && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Within $100 Budget
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Payment Guard Authorization Column */}
          <div className="md:col-span-5 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">Payment Guard Authorization</h2>

            {selectedProduct && guardResult ? (
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-semibold text-slate-300">Decision Status</div>
                  <span
                    className={`text-[10px] font-bold uppercase px-2.5 py-1 rounded-full border ${
                      guardResult.decision === 'ALLOW'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}
                  >
                    {guardResult.decision}
                  </span>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                  <div className="text-xs font-semibold text-slate-200">{guardResult.reason}</div>
                  <div className="text-[11px] text-slate-400 space-y-1">
                    <div>• Single Transaction Budget: $100.00 Limit</div>
                    <div>• Merchant Safety Score: 98% (Nova Electronics)</div>
                    <div>• Category: Audio (Allowed)</div>
                  </div>
                </div>

                {/* Purchase Action */}
                {!purchaseSuccess ? (
                  <button
                    onClick={handleExecuteGuardedPurchase}
                    disabled={isExecuting || !guardResult.is_allowed}
                    className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
                  >
                    <CreditCard className="w-4 h-4" />
                    <span>
                      {isExecuting
                        ? 'Creating & Capturing PayPal Order...'
                        : `Authorize Payment with PayPal ($${selectedProduct.price.toFixed(2)})`}
                    </span>
                  </button>
                ) : (
                  <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 space-y-2.5">
                    <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs">
                      <ShieldCheck className="w-4 h-4" />
                      <span>Payment Captured & Verified by PayPal</span>
                    </div>
                    <div className="text-[11px] text-slate-300 font-mono">
                      Capture ID: {purchaseSuccess.capture_id}
                    </div>
                    <button
                      onClick={() => setActiveTab('transactions')}
                      className="w-full py-1.5 mt-2 rounded bg-slate-900 text-slate-200 text-xs font-medium border border-slate-700 hover:bg-slate-800 transition-colors"
                    >
                      View in Transaction Explorer
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-400">
                Select a product to evaluate Payment Guard authorization rules.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
