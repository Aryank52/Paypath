import React from 'react';
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

export const App: React.FC = () => {
  const { activeTab, persona } = useStore();

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
            {activeTab === 'merchants' && <MerchantPortal />}
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
