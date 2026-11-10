import { create } from 'zustand';
import { Transaction, ReclaimCase } from '../types';

export type ActiveTab =
  | 'overview'
  | 'transactions'
  | 'shopping'
  | 'reclaim'
  | 'guard'
  | 'recovery'
  | 'merchants'
  | 'agents'
  | 'audit'
  | 'system';

export type UserPersona = 'SHOPPER' | 'MERCHANT_ADMIN' | 'PLATFORM_ADMIN';

interface AppState {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  persona: UserPersona;
  setPersona: (persona: UserPersona) => void;
  selectedTransaction: Transaction | null;
  setSelectedTransaction: (tx: Transaction | null) => void;
  activeReclaimCase: ReclaimCase | null;
  setActiveReclaimCase: (c: ReclaimCase | null) => void;
  isCommandCenterOpen: boolean;
  setIsCommandCenterOpen: (open: boolean) => void;
  notificationCount: number;
  setNotificationCount: (count: number) => void;
  prefetchedTxId: string | null;
  setPrefetchedTxId: (id: string | null) => void;
  legalModal: 'privacy' | 'terms' | null;
  setLegalModal: (modal: 'privacy' | 'terms' | null) => void;
}

export const useStore = create<AppState>((set) => ({
  activeTab: 'overview',
  setActiveTab: (tab) => set({ activeTab: tab }),
  persona: 'SHOPPER',
  setPersona: (persona) => set({ persona }),
  selectedTransaction: null,
  setSelectedTransaction: (tx) => set({ selectedTransaction: tx }),
  activeReclaimCase: null,
  setActiveReclaimCase: (c) => set({ activeReclaimCase: c }),
  isCommandCenterOpen: false,
  setIsCommandCenterOpen: (open) => set({ isCommandCenterOpen: open }),
  notificationCount: 2,
  setNotificationCount: (count) => set({ notificationCount: count }),
  prefetchedTxId: null,
  setPrefetchedTxId: (id) => set({ prefetchedTxId: id }),
  legalModal: null,
  setLegalModal: (modal) => set({ legalModal: modal }),
}));
