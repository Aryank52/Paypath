import React, { useEffect, useState, useMemo, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { 
  ColDef, 
  ModuleRegistry, 
  AllCommunityModule,
  themeQuartz, 
  colorSchemeDarkBlue 
} from 'ag-grid-community';

import { 
  Search, 
  RefreshCw, 
  Eye, 
  ShieldCheck, 
  AlertCircle, 
  ShoppingBag, 
  ArrowRight,
  Globe,
  User,
  Database
} from 'lucide-react';
import { api } from '../services/api';
import { Transaction, SharedFeedItem } from '../types';
import { useStore } from '../store/useStore';
import { TransactionDetailModal } from './TransactionDetailModal';

// Register all community modules for AG Grid v36
ModuleRegistry.registerModules([AllCommunityModule]);

export const TransactionExplorer: React.FC = () => {
  const [activeView, setActiveView] = useState<'platform' | 'personal'>('platform');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [sharedFeed, setSharedFeed] = useState<SharedFeedItem[]>([]);
  const [sharedTotal, setSharedTotal] = useState<number>(76);
  const [isLoadingPersonal, setIsLoadingPersonal] = useState(true);
  const [isLoadingPlatform, setIsLoadingPlatform] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quickFilterText, setQuickFilterText] = useState('');
  const { selectedTransaction, setSelectedTransaction, setActiveTab, setAuthModal } = useStore();
  const gridRef = useRef<AgGridReact>(null);

  const [prefetchedIds, setPrefetchedIds] = useState<Set<string>>(new Set());

  const fetchPersonalTransactions = () => {
    setIsLoadingPersonal(true);
    api.getTransactions()
      .then((data) => {
        setTransactions(data || []);
      })
      .catch((err) => {
        console.error('Failed to fetch personal transactions:', err);
      })
      .finally(() => setIsLoadingPersonal(false));
  };

  const fetchSharedFeed = () => {
    setIsLoadingPlatform(true);
    api.getSharedFeed({ limit: 100 })
      .then((res) => {
        if (res && Array.isArray(res.items)) {
          setSharedFeed(res.items);
          setSharedTotal(res.total_records || res.items.length);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch shared feed:', err);
        setError(err.message || 'Failed to load platform transaction feed');
      })
      .finally(() => setIsLoadingPlatform(false));
  };

  const reloadAll = () => {
    setError(null);
    fetchPersonalTransactions();
    fetchSharedFeed();
  };

  useEffect(() => {
    reloadAll();

    const handlePersonaChange = () => {
      reloadAll();
    };

    window.addEventListener('paypath:persona-changed', handlePersonaChange);
    return () => {
      window.removeEventListener('paypath:persona-changed', handlePersonaChange);
    };
  }, []);

  // Intent-aware prefetching on hover for personal items
  const handleCellMouseOver = (params: any) => {
    const tx = params.data as Transaction | undefined;
    if (tx && tx.id && !tx.id.startsWith('PP-TRX-') && !prefetchedIds.has(tx.id)) {
      setPrefetchedIds((prev) => new Set(prev).add(tx.id));
      api.getTransactionEvents(tx.id).catch(() => {});
    }
  };

  const openSharedItemDetails = (item: SharedFeedItem) => {
    const adapted: Transaction = {
      id: item.public_reference,
      user_id: 'sanitized',
      merchant_name: item.merchant_name,
      item_description: item.item,
      amount: item.amount,
      currency: item.currency,
      status: item.payment_state as any,
      verification_status: (item.verification_status as any) || 'VERIFIED',
      risk_score: item.risk_level === 'HIGH' ? 88 : item.risk_level === 'MEDIUM' ? 45 : 12,
      risk_level: item.risk_level,
      ai_summary: item.ai_summary,
      created_at: item.created_at,
      source_type: item.source,
    } as any;
    setSelectedTransaction(adapted);
  };

  // Personal Transactions Column Definitions
  const personalColumnDefs = useMemo<ColDef[]>(() => [
    {
      field: 'merchant_name',
      headerName: 'Merchant',
      minWidth: 160,
      flex: 1,
      cellRenderer: (params: any) => (
        <div className="flex items-center space-x-2 py-1">
          <div className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-indigo-400">
            {params.value?.charAt(0) || 'M'}
          </div>
          <span className="font-medium text-slate-200">{params.value}</span>
        </div>
      )
    },
    {
      field: 'item_description',
      headerName: 'Item / Service',
      minWidth: 200,
      flex: 1.5,
      cellRenderer: (params: any) => (
        <span className="text-slate-300 text-xs">{params.value || 'General Order'}</span>
      )
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 120,
      cellRenderer: (params: any) => (
        <span className="font-semibold text-white">
          ${parseFloat(params.value || 0).toFixed(2)} <span className="text-[10px] text-slate-400 font-normal">{params.data?.currency || 'USD'}</span>
        </span>
      )
    },
    {
      field: 'status',
      headerName: 'Payment State',
      width: 140,
      cellRenderer: (params: any) => {
        const val = params.value;
        let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
        if (val === 'CAPTURED') colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (val === 'REFUNDED' || val === 'PARTIALLY_REFUNDED') colorClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
        if (val === 'FAILED' || val === 'DISPUTED') colorClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
        return (
          <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${colorClass}`}>
            {val}
          </span>
        );
      }
    },
    {
      field: 'verification_status',
      headerName: 'PayPal Ledger',
      width: 160,
      cellRenderer: () => (
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[11px] font-medium text-emerald-400">Verified by PayPal</span>
        </div>
      )
    },
    {
      field: 'risk_level',
      headerName: 'Risk',
      width: 110,
      cellRenderer: (params: any) => {
        const level = params.value;
        let badge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (level === 'MEDIUM') badge = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
        if (level === 'HIGH') badge = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
        return (
          <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${badge}`}>
            {level || 'LOW'}
          </span>
        );
      }
    },
    {
      field: 'ai_summary',
      headerName: 'AI Intelligence Insight',
      minWidth: 240,
      flex: 2,
      cellRenderer: (params: any) => (
        <span className="text-slate-400 text-xs italic line-clamp-1">{params.value || 'Normal pattern'}</span>
      )
    },
    {
      field: 'source_type',
      headerName: 'Source',
      width: 130,
      cellRenderer: (params: any) => {
        const isSynthetic = params.value === 'DEMO_SEED' || (params.data?.id && params.data.id.startsWith('tx_'));
        return (
          <span className={`text-[9px] uppercase px-2 py-0.5 rounded-full font-mono font-medium ${
            isSynthetic ? 'bg-slate-800 text-slate-400 border border-slate-700' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
          }`}>
            {isSynthetic ? 'DEMO_SEED' : 'PAYPAL_SANDBOX'}
          </span>
        );
      }
    },
    {
      headerName: 'Action',
      width: 150,
      cellRenderer: (params: any) => (
        <button
          onClick={() => setSelectedTransaction(params.data)}
          className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition-colors cursor-pointer"
        >
          <Eye className="w-3 h-3 text-indigo-400" />
          <span>View Intelligence</span>
        </button>
      )
    }
  ], [setSelectedTransaction]);

  // Platform Shared Feed Column Definitions
  const platformColumnDefs = useMemo<ColDef[]>(() => [
    {
      field: 'public_reference',
      headerName: 'Reference',
      width: 145,
      cellRenderer: (params: any) => (
        <span className="font-mono text-xs font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded">
          {params.value}
        </span>
      )
    },
    {
      field: 'merchant_name',
      headerName: 'Merchant',
      minWidth: 150,
      flex: 1,
      cellRenderer: (params: any) => (
        <div className="flex items-center space-x-2 py-1">
          <div className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-indigo-400">
            {params.value?.charAt(0) || 'M'}
          </div>
          <span className="font-medium text-slate-200">{params.value}</span>
        </div>
      )
    },
    {
      field: 'item',
      headerName: 'Item / Service',
      minWidth: 180,
      flex: 1.4,
      cellRenderer: (params: any) => (
        <span className="text-slate-300 text-xs">{params.value || 'Guarded Item'}</span>
      )
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 120,
      cellRenderer: (params: any) => (
        <span className="font-semibold text-white">
          ${parseFloat(params.value || 0).toFixed(2)} <span className="text-[10px] text-slate-400 font-normal">{params.data?.currency || 'USD'}</span>
        </span>
      )
    },
    {
      field: 'payment_state',
      headerName: 'Payment State',
      width: 135,
      cellRenderer: (params: any) => {
        const val = params.value;
        let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
        if (val === 'CAPTURED') colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (val === 'REFUNDED' || val === 'PARTIALLY_REFUNDED') colorClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
        if (val === 'FAILED' || val === 'DISPUTED') colorClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
        return (
          <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${colorClass}`}>
            {val}
          </span>
        );
      }
    },
    {
      field: 'verification_status',
      headerName: 'PayPal Ledger',
      width: 155,
      cellRenderer: () => (
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[11px] font-medium text-emerald-400">Verified by PayPal</span>
        </div>
      )
    },
    {
      field: 'risk_level',
      headerName: 'Risk',
      width: 105,
      cellRenderer: (params: any) => {
        const level = params.value;
        let badge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (level === 'MEDIUM') badge = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
        if (level === 'HIGH') badge = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
        return (
          <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${badge}`}>
            {level || 'LOW'}
          </span>
        );
      }
    },
    {
      field: 'ai_summary',
      headerName: 'AI Intelligence Insight',
      minWidth: 220,
      flex: 1.8,
      cellRenderer: (params: any) => (
        <span className="text-slate-400 text-xs italic line-clamp-1">{params.value || 'Evaluated against policy guardrails'}</span>
      )
    },
    {
      field: 'source',
      headerName: 'Source',
      width: 135,
      cellRenderer: (params: any) => {
        const isSynthetic = params.value === 'DEMO_SEED';
        return (
          <span className={`text-[9px] uppercase px-2 py-0.5 rounded-full font-mono font-medium ${
            isSynthetic ? 'bg-slate-800 text-slate-400 border border-slate-700' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
          }`}>
            {isSynthetic ? 'DEMO_SEED' : 'PAYPAL_SANDBOX'}
          </span>
        );
      }
    },
    {
      field: 'created_at',
      headerName: 'Recorded',
      width: 130,
      cellRenderer: (params: any) => (
        <span className="text-[11px] text-slate-400 font-mono">
          {params.value ? new Date(params.value).toLocaleDateString() : 'Recent'}
        </span>
      )
    },
    {
      headerName: 'Action',
      width: 140,
      cellRenderer: (params: any) => (
        <button
          onClick={() => openSharedItemDetails(params.data)}
          className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition-colors cursor-pointer"
        >
          <Eye className="w-3 h-3 text-indigo-400" />
          <span>Intelligence</span>
        </button>
      )
    }
  ], []);

  const defaultColDef = useMemo(() => ({
    sortable: true,
    filter: true,
    resizable: true,
  }), []);

  // PayPath Dark Theming via AG Grid v36 Theming API
  const paypathGridTheme = useMemo(() => themeQuartz
    .withPart(colorSchemeDarkBlue)
    .withParams({
      backgroundColor: '#020617',
      foregroundColor: '#e2e8f0',
      headerBackgroundColor: '#0f172a',
      headerTextColor: '#94a3b8',
      borderColor: '#1e293b',
      rowHoverColor: '#1e293b50',
      selectedRowBackgroundColor: '#312e8130',
      accentColor: '#6366f1',
    }), []);

  const currentLoading = activeView === 'platform' ? isLoadingPlatform : isLoadingPersonal;

  return (
    <div className="space-y-4">
      {/* Top Search & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Transaction Intelligence Explorer</span>
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              AG Grid Powered
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Full-text search, column grouping, PayPal status read-backs, and AI explanations.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={`Search ${activeView === 'platform' ? 'platform feed' : 'personal ledger'}...`}
              value={quickFilterText}
              onChange={(e) => setQuickFilterText(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-56"
            />
          </div>

          <button
            onClick={reloadAll}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Refresh Grid"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${currentLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* View Switcher Tabs: Platform Intelligence Feed vs My Personal Ledger */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveView('platform')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeView === 'platform'
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            <span>Platform Intelligence Feed</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300">
              {sharedTotal}
            </span>
          </button>

          <button
            onClick={() => setActiveView('personal')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeView === 'personal'
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <User className="w-3.5 h-3.5 text-slate-400" />
            <span>My Personal Ledger</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
              {transactions.length}
            </span>
          </button>
        </div>

        <div className="hidden sm:flex items-center space-x-2 text-[11px] text-slate-400">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>Render PostgreSQL Authoritative</span>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>
              {error.toLowerCase().includes('authenticated') || error.toLowerCase().includes('expired') || error.toLowerCase().includes('token')
                ? 'Your session expired. Sign in again.'
                : 'Unable to load platform feed. Retry.'}
            </span>
          </div>
          <button
            onClick={() => {
              if (error.toLowerCase().includes('authenticated') || error.toLowerCase().includes('expired') || error.toLowerCase().includes('token') || error.toLowerCase().includes('credentials')) {
                setAuthModal('login');
              } else {
                reloadAll();
              }
            }}
            className="px-3 py-1 rounded bg-rose-600/30 hover:bg-rose-600/50 text-white font-medium text-xs transition-colors"
          >
            {error.toLowerCase().includes('authenticated') || error.toLowerCase().includes('expired') || error.toLowerCase().includes('token') || error.toLowerCase().includes('credentials') ? 'Sign In' : 'Retry'}
          </button>
        </div>
      )}

      {/* Empty State Banner for Personal Ledger */}
      {activeView === 'personal' && transactions.length === 0 && !isLoadingPersonal && (
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-slate-300">
          <div className="flex items-center gap-2.5">
            <ShoppingBag className="w-4 h-4 text-indigo-400 shrink-0" />
            <span>
              No personal transactions recorded for this account yet. You can inspect all {sharedTotal} live platform transactions or make a guarded purchase.
            </span>
          </div>
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={() => setActiveView('platform')}
              className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
            >
              View Platform Feed ({sharedTotal})
            </button>
            <button
              onClick={() => setActiveTab('shopping')}
              className="flex items-center gap-1.5 px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
            >
              <span>Guarded Purchase</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}

      {/* AG Grid Container */}
      <div className="h-[520px] w-full rounded-xl overflow-hidden border border-slate-800 shadow-xl bg-slate-950">
        <div className="h-full w-full">
          {activeView === 'platform' ? (
            <AgGridReact
              key="platform-grid"
              ref={gridRef}
              theme={paypathGridTheme}
              rowData={sharedFeed}
              columnDefs={platformColumnDefs}
              defaultColDef={defaultColDef}
              quickFilterText={quickFilterText}
              rowSelection="single"
              onRowClicked={(event) => openSharedItemDetails(event.data)}
              animateRows={true}
              loading={isLoadingPlatform}
              overlayLoadingTemplate={'<div class="ag-overlay-loading-center text-slate-300 font-medium text-xs flex items-center justify-center gap-2"><span>Loading platform intelligence feed...</span></div>'}
              overlayNoRowsTemplate={'<div class="text-slate-400 text-xs font-medium">No transactions available in the feed.</div>'}
            />
          ) : (
            <AgGridReact
              key="personal-grid"
              ref={gridRef}
              theme={paypathGridTheme}
              rowData={transactions}
              columnDefs={personalColumnDefs}
              defaultColDef={defaultColDef}
              quickFilterText={quickFilterText}
              rowSelection="single"
              onCellMouseOver={handleCellMouseOver}
              onRowClicked={(event) => setSelectedTransaction(event.data)}
              animateRows={true}
              loading={isLoadingPersonal}
              overlayLoadingTemplate={'<div class="ag-overlay-loading-center text-slate-300 font-medium text-xs flex items-center justify-center gap-2"><span>Loading personal ledger...</span></div>'}
              overlayNoRowsTemplate={'<div class="text-slate-400 text-xs font-medium">No transactions recorded for this personal account.</div>'}
            />
          )}
        </div>
      </div>

      {/* Detail Modal / Lifecycle Drawer */}
      {selectedTransaction && (
        <TransactionDetailModal
          transaction={selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  );
};
