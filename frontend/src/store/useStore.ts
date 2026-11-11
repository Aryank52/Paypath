import { create } from 'zustand';
import { Transaction, ReclaimCase, UserProfile } from '../types';

export type ActiveTab =
  | 'landing'
  | 'overview'
  | 'transactions'
  | 'shopping'
  | 'reclaim'
  | 'guard'
  | 'recovery'
  | 'merchants'
  | 'agents'
  | 'audit'
  | 'system'
  | 'profile'
  | 'security';

export type UserPersona = 'SHOPPER' | 'MERCHANT_ADMIN' | 'PLATFORM_ADMIN';

export type AuthModalType =
  | 'login'
  | 'signup'
  | 'forgot-password'
  | 'reset-password'
  | 'verify-email'
  | 'mfa'
  | null;

interface AppState {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  persona: UserPersona;
  setPersona: (persona: UserPersona) => void;
  isAuthenticated: boolean;
  currentUser: UserProfile | null;
  authModal: AuthModalType;
  setAuthModal: (modal: AuthModalType) => void;
  mfaPending: { user_id: string; email: string } | null;
  setMfaPending: (data: { user_id: string; email: string } | null) => void;
  resetToken: string | null;
  setResetToken: (token: string | null) => void;
  verificationToken: string | null;
  setVerificationToken: (token: string | null) => void;
  loginUser: (token: string, user: UserProfile) => void;
  logoutUser: () => void;
  updateCurrentUser: (updates: Partial<UserProfile>) => void;
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
  legalModal: 'privacy' | 'terms' | 'dpdp' | 'refund' | 'security' | null;
  setLegalModal: (modal: 'privacy' | 'terms' | 'dpdp' | 'refund' | 'security' | null) => void;
}

const getInitialAuth = () => {
  try {
    const token = localStorage.getItem('paypath_token');
    const userRaw = localStorage.getItem('paypath_user');
    if (token && userRaw) {
      return { token, user: JSON.parse(userRaw) as UserProfile };
    }
  } catch {
    // ignore parse error
  }
  return { token: null, user: null };
};

const initialAuth = getInitialAuth();

export const useStore = create<AppState>((set) => ({
  activeTab: initialAuth.token ? 'overview' : 'landing',
  setActiveTab: (tab) => set({ activeTab: tab }),
  persona: (initialAuth.user?.role as UserPersona) || 'SHOPPER',
  setPersona: (persona) => set({ persona }),
  isAuthenticated: !!initialAuth.token,
  currentUser: initialAuth.user,
  authModal: null,
  setAuthModal: (modal) => set({ authModal: modal }),
  mfaPending: null,
  setMfaPending: (data) => set({ mfaPending: data }),
  resetToken: null,
  setResetToken: (token) => set({ resetToken: token }),
  verificationToken: null,
  setVerificationToken: (token) => set({ verificationToken: token }),

  loginUser: (token: string, user: UserProfile) => {
    localStorage.setItem('paypath_token', token);
    localStorage.setItem('paypath_user', JSON.stringify(user));
    const persona: UserPersona =
      user.role === 'PLATFORM_ADMIN'
        ? 'PLATFORM_ADMIN'
        : user.role === 'MERCHANT_ADMIN'
        ? 'MERCHANT_ADMIN'
        : 'SHOPPER';
    set({
      isAuthenticated: true,
      currentUser: user,
      persona,
      activeTab: 'overview',
      authModal: null,
      mfaPending: null,
    });
  },

  logoutUser: () => {
    localStorage.removeItem('paypath_token');
    localStorage.removeItem('paypath_user');
    set({
      isAuthenticated: false,
      currentUser: null,
      persona: 'SHOPPER',
      activeTab: 'landing',
      authModal: null,
      mfaPending: null,
    });
  },

  updateCurrentUser: (updates) => {
    set((state) => {
      if (!state.currentUser) return state;
      const updated = { ...state.currentUser, ...updates };
      localStorage.setItem('paypath_user', JSON.stringify(updated));
      return { currentUser: updated };
    });
  },

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
