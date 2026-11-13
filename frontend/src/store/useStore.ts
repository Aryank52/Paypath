import { create } from 'zustand';
import { Transaction, ReclaimCase, UserProfile, DemoSessionResponse } from '../types';

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
  isDemoMode: boolean;
  setIsDemoMode: (isDemo: boolean) => void;
  isSwitchingPersona: boolean;
  setIsSwitchingPersona: (switching: boolean) => void;
  allowedPersonas: UserPersona[];
  setAllowedPersonas: (personas: UserPersona[]) => void;
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
  enterDemoSession: (session: DemoSessionResponse) => void;
  exitDemoSession: () => void;
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
    const isDemo = localStorage.getItem('paypath_is_demo') === 'true';
    if (token && userRaw) {
      return { token, user: JSON.parse(userRaw) as UserProfile, isDemo };
    }
  } catch {
    // ignore parse error
  }
  return { token: null, user: null, isDemo: false };
};

const initialAuth = getInitialAuth();

export const useStore = create<AppState>((set) => ({
  activeTab: initialAuth.token ? 'overview' : 'landing',
  setActiveTab: (tab) => set({ activeTab: tab }),
  persona: (initialAuth.user?.role as UserPersona) || 'SHOPPER',
  setPersona: (persona) => set({ persona }),
  isAuthenticated: !!initialAuth.token,
  isDemoMode: initialAuth.isDemo,
  setIsDemoMode: (isDemo) => set({ isDemoMode: isDemo }),
  isSwitchingPersona: false,
  setIsSwitchingPersona: (switching) => set({ isSwitchingPersona: switching }),
  allowedPersonas: initialAuth.isDemo
    ? ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN']
    : initialAuth.user?.role === 'PLATFORM_ADMIN'
    ? ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN']
    : initialAuth.user?.role === 'MERCHANT_ADMIN'
    ? ['SHOPPER', 'MERCHANT_ADMIN']
    : ['SHOPPER'],
  setAllowedPersonas: (personas) => set({ allowedPersonas: personas }),
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
    localStorage.removeItem('paypath_is_demo');
    const persona: UserPersona =
      user.role === 'PLATFORM_ADMIN'
        ? 'PLATFORM_ADMIN'
        : user.role === 'MERCHANT_ADMIN'
        ? 'MERCHANT_ADMIN'
        : 'SHOPPER';
    set({
      isAuthenticated: true,
      isDemoMode: false,
      currentUser: user,
      persona,
      allowedPersonas:
        user.role === 'PLATFORM_ADMIN'
          ? ['SHOPPER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN']
          : user.role === 'MERCHANT_ADMIN'
          ? ['SHOPPER', 'MERCHANT_ADMIN']
          : ['SHOPPER'],
      activeTab: 'overview',
      authModal: null,
      mfaPending: null,
    });
  },

  enterDemoSession: (session: DemoSessionResponse) => {
    localStorage.setItem('paypath_token', session.access_token);
    localStorage.setItem('paypath_is_demo', 'true');
    const userObj: UserProfile = {
      id: session.user_id,
      email: session.email,
      role: session.role as any,
      full_name: session.full_name,
      preferred_currency: 'USD',
      is_active: true,
      email_verified: true,
      mfa_enabled: false,
      is_demo: true
    };
    localStorage.setItem('paypath_user', JSON.stringify(userObj));
    set({
      isAuthenticated: true,
      isDemoMode: true,
      currentUser: userObj,
      persona: session.active_persona,
      allowedPersonas: session.allowed_personas,
      activeTab: 'overview',
      authModal: null,
      mfaPending: null,
    });
  },

  exitDemoSession: () => {
    localStorage.removeItem('paypath_token');
    localStorage.removeItem('paypath_user');
    localStorage.removeItem('paypath_is_demo');
    set({
      isAuthenticated: false,
      isDemoMode: false,
      currentUser: null,
      persona: 'SHOPPER',
      allowedPersonas: ['SHOPPER'],
      activeTab: 'landing',
      authModal: null,
      mfaPending: null,
    });
  },

  logoutUser: () => {
    localStorage.removeItem('paypath_token');
    localStorage.removeItem('paypath_user');
    localStorage.removeItem('paypath_is_demo');
    set({
      isAuthenticated: false,
      isDemoMode: false,
      currentUser: null,
      persona: 'SHOPPER',
      allowedPersonas: ['SHOPPER'],
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
