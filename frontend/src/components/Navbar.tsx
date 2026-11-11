import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Command, 
  Bell, 
  Search, 
  UserCheck, 
  Store, 
  SlidersHorizontal,
  LogOut,
  User,
  Lock,
  ChevronDown
} from 'lucide-react';
import { useStore, UserPersona } from '../store/useStore';

export const Navbar: React.FC = () => {
  const { 
    isCommandCenterOpen, 
    setIsCommandCenterOpen, 
    notificationCount, 
    persona, 
    setPersona, 
    activeTab, 
    setActiveTab, 
    isAuthenticated, 
    currentUser, 
    logoutUser, 
    setAuthModal 
  } = useStore();

  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const togglePersona = (newPersona: UserPersona) => {
    setPersona(newPersona);
    if (newPersona === 'MERCHANT_ADMIN') {
      setActiveTab('merchants');
    } else if (newPersona === 'PLATFORM_ADMIN') {
      setActiveTab('system');
    } else {
      setActiveTab('overview');
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Tagline - Clickable to Home / Dashboard */}
      <div 
        onClick={() => setActiveTab(isAuthenticated ? 'overview' : 'landing')}
        className="flex items-center space-x-3 cursor-pointer group"
      >
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight text-white group-hover:text-indigo-300 transition-colors">PAYPATH</span>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              AI Transaction Intelligence & Agentic Commerce
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Understand. Decide. Act. Verify.</p>
        </div>
      </div>

      {/* Middle Command Trigger */}
      {isAuthenticated && (
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
      )}

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Unauthenticated State */}
        {!isAuthenticated ? (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAuthModal('login')}
              className="px-4 py-2 rounded-xl text-slate-300 hover:text-white text-xs font-medium hover:bg-slate-900 transition-colors cursor-pointer"
            >
              Sign In
            </button>
            <button
              onClick={() => setAuthModal('signup')}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
            >
              Get Started
            </button>
          </div>
        ) : (
          <>
            {/* Persona Switcher */}
            <div className="hidden sm:flex items-center bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-xs font-medium">
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
                <span>Merchant</span>
              </button>
              <button
                onClick={() => togglePersona('PLATFORM_ADMIN')}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  persona === 'PLATFORM_ADMIN'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <SlidersHorizontal className="w-3 h-3" />
                <span>Control Center</span>
              </button>
            </div>

            {/* Sandbox Indicator */}
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
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

            {/* User Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2.5 pl-3 border-l border-slate-800 hover:opacity-90 transition-opacity cursor-pointer"
              >
                <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-xs font-semibold text-indigo-300">
                  {currentUser?.full_name ? currentUser.full_name.charAt(0).toUpperCase() : 'A'}
                </div>
                <div className="hidden lg:block text-left">
                  <div className="text-xs font-medium text-slate-200">
                    {currentUser?.full_name || 'Alex Chen'}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {persona === 'PLATFORM_ADMIN' ? 'Platform Admin' : persona === 'MERCHANT_ADMIN' ? 'Merchant Admin' : 'Verified Shopper'}
                  </div>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden lg:block" />
              </button>

              {userMenuOpen && (
                <div 
                  className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl py-2 z-50 text-xs animate-in fade-in duration-150"
                  onMouseLeave={() => setUserMenuOpen(false)}
                >
                  <div className="px-3 py-2 border-b border-slate-800 text-[11px] text-slate-400">
                    Signed in as <span className="font-semibold text-white block truncate">{currentUser?.email || 'demo@paypath.finance'}</span>
                  </div>
                  <button
                    onClick={() => { setActiveTab('profile'); setUserMenuOpen(false); }}
                    className="w-full px-3 py-2 text-left hover:bg-slate-800 flex items-center gap-2 text-slate-300 hover:text-white cursor-pointer"
                  >
                    <User className="w-3.5 h-3.5" />
                    <span>My Profile</span>
                  </button>
                  <button
                    onClick={() => { setActiveTab('security'); setUserMenuOpen(false); }}
                    className="w-full px-3 py-2 text-left hover:bg-slate-800 flex items-center gap-2 text-slate-300 hover:text-white cursor-pointer"
                  >
                    <Lock className="w-3.5 h-3.5" />
                    <span>Security Center</span>
                  </button>
                  <div className="border-t border-slate-800 my-1"></div>
                  <button
                    onClick={() => { logoutUser(); setUserMenuOpen(false); }}
                    className="w-full px-3 py-2 text-left hover:bg-slate-800 flex items-center gap-2 text-rose-400 hover:text-rose-300 cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </header>
  );
};
