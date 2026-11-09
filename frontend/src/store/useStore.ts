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
  | 'audit';

interface AppState {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  selectedTransaction: Transaction | null;
  setSelectedTransaction: (tx: Transaction | null) => void;
  activeReclaimCase: ReclaimCase | null;
  setActiveReclaimCase: (c: ReclaimCase | null) => void;
  isCommandCenterOpen: boolean;
  setIsCommandCenterOpen: (open: boolean) => void;
  notificationCount: number;
  setNotificationCount: (count: number) => void;
}

export const useStore = create<AppState>((set) => ({
  activeTab: 'overview',
  setActiveTab: (tab) => set({ activeTab: tab }),
  selectedTransaction: null,
  setSelectedTransaction: (tx) => set({ selectedTransaction: tx }),
  activeReclaimCase: null,
  setActiveReclaimCase: (c) => set({ activeReclaimCase: c }),
  isCommandCenterOpen: false,
  setIsCommandCenterOpen: (open) => set({ isCommandCenterOpen: open }),
  notificationCount: 2,
  setNotificationCount: (count) => set({ notificationCount: count }),
}));
