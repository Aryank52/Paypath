import React from 'react';
import {
  LayoutDashboard,
  ReceiptText,
  ShoppingBag,
  RotateCcw,
  ShieldAlert,
  Repeat,
  Store,
  Cpu,
  FileCheck2,
  Server
} from 'lucide-react';
import { useStore, ActiveTab } from '../store/useStore';

interface NavItem {
  id: ActiveTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  allowedPersonas?: ('SHOPPER' | 'MERCHANT_ADMIN' | 'PLATFORM_ADMIN')[];
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, allowedPersonas: ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN'] },
  { id: 'transactions', label: 'Transactions', icon: ReceiptText, badge: 'AG Grid', allowedPersonas: ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN'] },
  { id: 'shopping', label: 'Guarded Shopping', icon: ShoppingBag, allowedPersonas: ['SHOPPER', 'PLATFORM_ADMIN'] },
  { id: 'guard', label: 'Payment Guard', icon: ShieldAlert, allowedPersonas: ['SHOPPER', 'PLATFORM_ADMIN'] },
  { id: 'recovery', label: 'Recovery Intel', icon: Repeat, allowedPersonas: ['SHOPPER', 'PLATFORM_ADMIN'] },
  { id: 'reclaim', label: 'RECLAIM Engine', icon: RotateCcw, badge: 'Hero', allowedPersonas: ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN'] },
  { id: 'merchants', label: 'Merchant Studio', icon: Store, allowedPersonas: ['MERCHANT_ADMIN', 'PLATFORM_ADMIN'] },
  { id: 'agents', label: 'Agent Traces', icon: Cpu, badge: 'Admin', allowedPersonas: ['PLATFORM_ADMIN'] },
  { id: 'audit', label: 'Audit Trail', icon: FileCheck2, badge: 'Admin', allowedPersonas: ['PLATFORM_ADMIN'] },
  { id: 'system', label: 'System Architecture', icon: Server, badge: 'Live', allowedPersonas: ['PLATFORM_ADMIN'] },
];

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, persona, setLegalModal } = useStore();

  const filteredItems = NAV_ITEMS.filter((item) => {
    if (!item.allowedPersonas) return true;
    return item.allowedPersonas.includes(persona);
  });

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4 flex flex-col justify-between h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="px-3 flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Intelligence Modes</p>
          <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-mono bg-slate-800 text-slate-400 border border-slate-700">
            {persona.replace('_', ' ')}
          </span>
        </div>

        <nav className="space-y-1">
          {filteredItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
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
                        : item.badge === 'Admin'
                        ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
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

      {/* Verified Badge & Legal Links Footer */}
      <div className="space-y-3">
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
          <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Verified by PayPal</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-relaxed">
            Dual-phase read-back verifications active on all mutations.
          </p>
        </div>

        <div className="px-2 flex items-center justify-between text-[10px] text-slate-500">
          <button
            onClick={() => setLegalModal('privacy')}
            className="hover:text-slate-300 transition-colors cursor-pointer"
          >
            Privacy Policy
          </button>
          <span>•</span>
          <button
            onClick={() => setLegalModal('terms')}
            className="hover:text-slate-300 transition-colors cursor-pointer"
          >
            Terms of Service
          </button>
          <span>•</span>
          <span>v1.0</span>
        </div>
      </div>
    </aside>
  );
};
