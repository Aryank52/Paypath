import React, { useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LandingPage } from './components/LandingPage';
import { OverviewDashboard } from './components/OverviewDashboard';
import { TransactionExplorer } from './components/TransactionExplorer';
import { ShoppingCenter } from './components/ShoppingCenter';
import { ReclaimResolutionCenter } from './components/ReclaimResolutionCenter';
import { PaymentGuardStudio } from './components/PaymentGuardStudio';
import { RecoveryIntelligence } from './components/RecoveryIntelligence';
import { MerchantPortal } from './components/MerchantPortal';
import { UserProfileView } from './components/UserProfileView';
import { SecurityCenterView } from './components/SecurityCenterView';
import { AgentTraceVisualizer } from './components/AgentTraceVisualizer';
import { AuditLogView } from './components/AuditLogView';
import { SystemIntelligenceView } from './components/SystemIntelligenceView';
import { AICommandCenterModal } from './components/AICommandCenterModal';
import { AuthModal } from './components/AuthModal';
import { LegalModal } from './components/LegalModal';
import { CookieBanner } from './components/CookieBanner';
import { Footer } from './components/Footer';
import { useStore } from './store/useStore';
import { api } from './services/api';
import { Store } from 'lucide-react';

export const App: React.FC = () => {
  const { activeTab, persona, currentUser, loginUser, logoutUser, setAuthModal } = useStore();

  useEffect(() => {
    // 1. Listen for auth expiration events dispatched on 401
    const handleAuthExpired = () => {
      logoutUser();
      setAuthModal('login');
    };
    window.addEventListener('paypath:auth-expired', handleAuthExpired);

    // 2. Proactively validate existing token with /auth/me on mount if present
    const token = localStorage.getItem('paypath_token');
    if (token) {
      api.getMe().catch(() => {
        // Stale or expired token: clear immediately to avoid empty/broken UI
        logoutUser();
      });
    }

    return () => {
      window.removeEventListener('paypath:auth-expired', handleAuthExpired);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar />

      {/* Landing Page (Public View) */}
      {activeTab === 'landing' ? (
        <main className="flex-1 overflow-y-auto">
          <LandingPage />
        </main>
      ) : (
        /* Authenticated Workspace */
        <div className="flex-1 flex overflow-hidden">
          {/* Navigation Sidebar */}
          <Sidebar />

          {/* Dynamic Screen Content */}
          <main className="flex-1 overflow-y-auto p-6 bg-[#0a0e1a]">
            {activeTab === 'overview' && <OverviewDashboard />}
            {activeTab === 'transactions' && <TransactionExplorer />}
            {activeTab === 'shopping' && <ShoppingCenter />}
            {activeTab === 'reclaim' && <ReclaimResolutionCenter />}
            {activeTab === 'guard' && <PaymentGuardStudio />}
            {activeTab === 'recovery' && <RecoveryIntelligence />}
            {activeTab === 'merchants' && (
              (currentUser?.role === 'MERCHANT_ADMIN' || currentUser?.role === 'PLATFORM_ADMIN') ? (
                <MerchantPortal />
              ) : (
                <div className="max-w-xl mx-auto my-12 p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-4 shadow-xl">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
                    <Store className="w-6 h-6" />
                  </div>
                  <h2 className="text-lg font-bold text-white">Merchant Administrator Access Required</h2>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    The Merchant Studio is restricted to verified merchant administrators (<span className="font-mono text-indigo-400">MERCHANT_ADMIN</span>) and platform operators. Your current active session is signed in as a Shopper (<span className="font-mono text-slate-300">{currentUser?.email || 'Guest'}</span>).
                  </p>
                  <div className="pt-2">
                    <button
                      onClick={() => setAuthModal('login')}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors cursor-pointer shadow-lg shadow-indigo-600/20"
                    >
                      Sign In as Merchant Administrator
                    </button>
                  </div>
                </div>
              )
            )}
            {activeTab === 'profile' && <UserProfileView />}
            {activeTab === 'security' && <SecurityCenterView />}
            
            {/* Protected Platform Admin Controls */}
            {activeTab === 'agents' && (
              persona === 'PLATFORM_ADMIN' ? <AgentTraceVisualizer /> : <OverviewDashboard />
            )}
            {activeTab === 'audit' && (
              persona === 'PLATFORM_ADMIN' ? <AuditLogView /> : <OverviewDashboard />
            )}
            {activeTab === 'system' && (
              persona === 'PLATFORM_ADMIN' ? <SystemIntelligenceView /> : <OverviewDashboard />
            )}
          </main>
        </div>
      )}

      {/* Global Product Footer */}
      <Footer />

      {/* Authentication Modal (Login, Signup, MFA, Password Reset, Email Verification) */}
      <AuthModal />

      {/* Global AI Command Modal with Voice Recognition */}
      <AICommandCenterModal />

      {/* Legal & Privacy Policy Modal */}
      <LegalModal />

      {/* Essential Storage & Privacy Notice Banner */}
      <CookieBanner />
    </div>
  );
};

export default App;
