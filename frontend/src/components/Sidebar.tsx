import React from 'react';
import {
  LayoutDashboard,
  ReceiptText,
  ShoppingBag,
  RotateCcw,
  ShieldAlert,
  Repeat,
  Cpu,
  FileCheck2
} from 'lucide-react';
import { useStore, ActiveTab } from '../store/useStore';

interface NavItem {
  id: ActiveTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', icon: ReceiptText, badge: 'AG Grid' },
  { id: 'shopping', label: 'Guarded Shopping', icon: ShoppingBag },
  { id: 'reclaim', label: 'RECLAIM Engine', icon: RotateCcw, badge: 'Hero' },
  { id: 'guard', label: 'Payment Guard', icon: ShieldAlert },
  { id: 'recovery', label: 'Recovery Intel', icon: Repeat },
  { id: 'agents', label: 'Agent Traces', icon: Cpu },
  { id: 'audit', label: 'Audit Trail', icon: FileCheck2 },
];

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab } = useStore();

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="px-3">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Intelligence Modes</p>
        </div>

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-semibold tracking-wider ${
                      item.badge === 'Hero'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Verified Badge Footer */}
      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
        <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Verified by PayPal</span>
        </div>
        <p className="text-[10px] text-slate-400 leading-relaxed">
          Dual-phase read-back verifications active on all mutations.
        </p>
      </div>
    </aside>
  );
};
