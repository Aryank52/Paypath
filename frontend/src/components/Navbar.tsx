import React from 'react';
import { ShieldCheck, Command, Bell, Search, UserCheck, Store } from 'lucide-react';
import { useStore } from '../store/useStore';

export const Navbar: React.FC = () => {
  const isCommandCenterOpen = useStore((state) => state.isCommandCenterOpen);
  const setIsCommandCenterOpen = useStore((state) => state.setIsCommandCenterOpen);
  const notificationCount = useStore((state) => state.notificationCount);
  const persona = useStore((state) => state.persona);
  const setPersona = useStore((state) => state.setPersona);
  const setActiveTab = useStore((state) => state.setActiveTab);

  const togglePersona = (newPersona: 'SHOPPER' | 'MERCHANT_ADMIN') => {
    setPersona(newPersona);
    if (newPersona === 'MERCHANT_ADMIN') {
      setActiveTab('merchants');
    } else {
      setActiveTab('overview');
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Tagline */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight text-white">PayPath</span>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              AI Commerce & Control
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Understand. Decide. Act. Verify.</p>
        </div>
      </div>

      {/* Middle Command Trigger */}
      <div className="flex-1 max-w-md mx-8 hidden md:block">
        <button
          onClick={() => setIsCommandCenterOpen(true)}
          className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 text-xs transition-all shadow-inner group cursor-pointer"
        >
          <div className="flex items-center space-x-2">
            <Search className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
            <span>Ask PayPath AI about transactions or policies...</span>
          </div>
          <div className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">
            <Command className="w-2.5 h-2.5" />
            <span>K</span>
          </div>
        </button>
      </div>

      {/* Status Badges & Controls */}
      <div className="flex items-center space-x-4">
        {/* Persona Switcher */}
        <div className="flex items-center bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-xs font-medium">
          <button
            onClick={() => togglePersona('SHOPPER')}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              persona === 'SHOPPER'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserCheck className="w-3 h-3" />
            <span>Shopper</span>
          </button>
          <button
            onClick={() => togglePersona('MERCHANT_ADMIN')}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              persona === 'MERCHANT_ADMIN'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Store className="w-3 h-3" />
            <span>Merchant Admin</span>
          </button>
        </div>

        {/* Sandbox Indicator */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>PayPal Sandbox Active</span>
        </div>

        {/* Notifications */}
        <button
          onClick={() => setActiveTab('reclaim')}
          className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-colors cursor-pointer"
        >
          <Bell className="w-4 h-4" />
          {notificationCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-amber-500"></span>
          )}
        </button>

        {/* User Pill */}
        <div className="flex items-center space-x-2.5 pl-3 border-l border-slate-800">
          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-200">
            {persona === 'SHOPPER' ? 'AM' : 'AG'}
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-medium text-slate-200">
              {persona === 'SHOPPER' ? 'Alex Mercer' : 'Apex Admin'}
            </div>
            <div className="text-[10px] text-slate-400">
              {persona === 'SHOPPER' ? 'Verified Shopper' : 'Merchant Portal'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
