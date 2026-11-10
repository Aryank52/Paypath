import React from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { OverviewDashboard } from './components/OverviewDashboard';
import { TransactionExplorer } from './components/TransactionExplorer';
import { ShoppingCenter } from './components/ShoppingCenter';
import { ReclaimResolutionCenter } from './components/ReclaimResolutionCenter';
import { PaymentGuardStudio } from './components/PaymentGuardStudio';
import { RecoveryIntelligence } from './components/RecoveryIntelligence';
import { MerchantPortal } from './components/MerchantPortal';
import { AgentTraceVisualizer } from './components/AgentTraceVisualizer';
import { AuditLogView } from './components/AuditLogView';
import { SystemIntelligenceView } from './components/SystemIntelligenceView';
import { AICommandCenterModal } from './components/AICommandCenterModal';
import { LegalModal } from './components/LegalModal';
import { useStore } from './store/useStore';

export const App: React.FC = () => {
  const { activeTab } = useStore();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar />

      {/* Main App Workspace */}
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
          {activeTab === 'agents' && <AgentTraceVisualizer />}
          {activeTab === 'audit' && <AuditLogView />}
          {activeTab === 'system' && <SystemIntelligenceView />}
        </main>
      </div>

      {/* Global AI Command Modal with Voice Recognition */}
      <AICommandCenterModal />

      {/* Legal & Privacy Policy Modal */}
      <LegalModal />
    </div>
  );
};

export default App;
