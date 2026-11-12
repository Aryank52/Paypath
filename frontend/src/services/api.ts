import {
  Transaction,
  TransactionEvent,
  ReclaimCase,
  EvidenceItem,
  Product,
  GuardEvaluation,
  SubscriptionItem,
  DuplicateSignal,
  UserProfile
} from '../types';

const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? 'https://paypath-8u9a.onrender.com' : '')
).replace(/\/$/, '');
const API_BASE = `${API_ORIGIN}/api/v1`;

export const getAuthHeaders = (isJson = true): HeadersInit => {
  const token = localStorage.getItem('paypath_token');
  const headers: Record<string, string> = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Authentication & User Profile
  login: async (data: { email: string; password: string; mfa_code?: string }) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Authentication failed');
    }
    return res.json();
  },

  register: async (data: {
    email: string;
    password: string;
    full_name?: string;
    mobile_number?: string;
  }) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  getMe: async (): Promise<UserProfile> => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to retrieve user profile');
    return res.json();
  },

  updateProfile: async (data: {
    full_name?: string;
    mobile_number?: string;
    preferred_currency?: string;
  }): Promise<UserProfile> => {
    const res = await fetch(`${API_BASE}/auth/profile`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update profile');
    }
    return res.json();
  },

  changePassword: async (data: { current_password: string; new_password: string }) => {
    const res = await fetch(`${API_BASE}/auth/password/change`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to change password');
    }
    return res.json();
  },

  setupMFA: async () => {
    const res = await fetch(`${API_BASE}/auth/mfa/setup`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to initiate MFA setup');
    return res.json();
  },

  enableMFA: async (code: string) => {
    const res = await fetch(`${API_BASE}/auth/mfa/enable`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ code })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid MFA code');
    }
    return res.json();
  },

  disableMFA: async (code: string) => {
    const res = await fetch(`${API_BASE}/auth/mfa/disable`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ code })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid MFA code');
    }
    return res.json();
  },

  requestPasswordReset: async (email: string) => {
    const res = await fetch(`${API_BASE}/auth/password-reset/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw new Error('Failed to request password reset');
    return res.json();
  },

  confirmPasswordReset: async (token: string, new_password: string) => {
    const res = await fetch(`${API_BASE}/auth/password-reset/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to reset password');
    }
    return res.json();
  },

  verifyEmail: async (token: string) => {
    const res = await fetch(`${API_BASE}/auth/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Email verification failed');
    }
    return res.json();
  },

  resendVerificationEmail: async (email: string) => {
    const res = await fetch(`${API_BASE}/auth/verify-email/resend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw new Error('Failed to dispatch verification email');
    return res.json();
  },

  // Transactions
  getTransactions: async (params?: { status?: string; risk_level?: string; merchant_name?: string }): Promise<Transaction[]> => {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.risk_level) query.append('risk_level', params.risk_level);
    if (params?.merchant_name) query.append('merchant_name', params.merchant_name);
    const res = await fetch(`${API_BASE}/transactions?${query.toString()}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch transactions');
    return res.json();
  },

  getTransaction: async (id: string): Promise<Transaction> => {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch transaction details');
    return res.json();
  },

  getTransactionEvents: async (id: string): Promise<TransactionEvent[]> => {
    const res = await fetch(`${API_BASE}/transactions/${id}/events`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch transaction events');
    return res.json();
  },

  // PayCore
  createOrder: async (data: {
    amount: number;
    currency?: string;
    merchant_name?: string;
    item_description?: string;
    user_intent_id?: string;
  }) => {
    const res = await fetch(`${API_BASE}/paycore/orders/create`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create order');
    }
    return res.json();
  },

  captureOrder: async (orderId: string) => {
    const res = await fetch(`${API_BASE}/paycore/orders/capture`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ order_id: orderId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to capture order');
    }
    return res.json();
  },

  refundPayment: async (data: { transaction_id: string; amount: number; reason?: string }) => {
    const res = await fetch(`${API_BASE}/paycore/refunds`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to execute refund');
    }
    return res.json();
  },

  verifyResource: async (resourceId: string, actionType: 'CAPTURE' | 'REFUND' = 'CAPTURE', expectedAmount = 89.0) => {
    const res = await fetch(`${API_BASE}/paycore/verify/${resourceId}?action_type=${actionType}&expected_amount=${expectedAmount}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to verify resource');
    return res.json();
  },

  // Shopping & Intent
  parseIntent: async (prompt: string) => {
    const res = await fetch(`${API_BASE}/intent/parse`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to parse intent');
    }
    return res.json();
  },

  searchProducts: async (category = 'headphones', budget = 100.0, purpose = 'travel'): Promise<Product[]> => {
    const res = await fetch(`${API_BASE}/shop/search?category=${encodeURIComponent(category)}&budget=${budget}&purpose=${encodeURIComponent(purpose)}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to search products');
    return res.json();
  },

  proposePurchase: async (data: {
    product_id: string;
    amount: number;
    merchant_name: string;
    category?: string;
    user_budget?: number;
  }) => {
    const res = await fetch(`${API_BASE}/shop/propose-purchase`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to evaluate purchase proposal');
    }
    return res.json();
  },

  // Payment Guard
  evaluateGuard: async (data: { amount: number; merchant_name: string; category?: string }): Promise<GuardEvaluation> => {
    const res = await fetch(`${API_BASE}/guard/evaluate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to evaluate guard');
    }
    return res.json();
  },

  // RECLAIM
  createReclaimCase: async (data: { transaction_id: string; issue_type: string; description: string }): Promise<ReclaimCase> => {
    const res = await fetch(`${API_BASE}/reclaim/cases`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create dispute case');
    }
    return res.json();
  },

  uploadEvidence: async (caseId: string, file: File): Promise<EvidenceItem> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/evidence`, {
      method: 'POST',
      headers: getAuthHeaders(false),
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload evidence');
    }
    return res.json();
  },

  evaluateCase: async (caseId: string) => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/evaluate`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to evaluate dispute case');
    }
    return res.json();
  },

  approveRefund: async (caseId: string) => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/approve`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to approve and execute refund');
    }
    return res.json();
  },

  getReclaimCases: async (): Promise<ReclaimCase[]> => {
    const res = await fetch(`${API_BASE}/reclaim/cases`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch reclaim cases');
    return res.json();
  },

  getCase: async (caseId: string): Promise<ReclaimCase> => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to get dispute case');
    return res.json();
  },

  // Recovery Intelligence
  getDuplicates: async (): Promise<DuplicateSignal[]> => {
    const res = await fetch(`${API_BASE}/recover/duplicates`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch duplicate signals');
    return res.json();
  },

  getSubscriptions: async (): Promise<SubscriptionItem[]> => {
    const res = await fetch(`${API_BASE}/recover/subscriptions`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch subscriptions');
    return res.json();
  },

  // Agents
  runCommerceWorkflow: async (prompt: string) => {
    const res = await fetch(`${API_BASE}/agents/run-commerce`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to run commerce workflow');
    }
    return res.json();
  },

  runReclaimWorkflow: async (data: any) => {
    const res = await fetch(`${API_BASE}/agents/run-reclaim`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to run reclaim workflow');
    }
    return res.json();
  },

  // Audit
  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/audit`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  // System Diagnostics & Database
  getSystemHealth: async () => {
    const res = await fetch(`${API_BASE}/system/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  getDatabaseInventory: async () => {
    const res = await fetch(`${API_BASE}/system/database`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch database inventory');
    return res.json();
  },

  getLineageTransactions: async () => {
    const res = await fetch(`${API_BASE}/system/lineage-transactions`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch lineage transactions');
    return res.json();
  },

  getTransactionLineage: async (id: string) => {
    const res = await fetch(`${API_BASE}/system/lineage/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch transaction lineage');
    return res.json();
  },

  // Machine Learning
  getMLModels: async () => {
    const res = await fetch(`${API_BASE}/ml/models`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch ML models');
    return res.json();
  },

  getMLFeatures: async () => {
    const res = await fetch(`${API_BASE}/ml/features`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch ML features');
    return res.json();
  },

  explainTransaction: async (id: string) => {
    const res = await fetch(`${API_BASE}/ml/explain/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to explain transaction');
    }
    return res.json();
  },

  predictRisk: async (data: {
    amount: number;
    merchant_name: string;
    item_description?: string;
    user_id?: string;
    is_subscription?: boolean;
  }) => {
    const res = await fetch(`${API_BASE}/ml/predict`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to run ML prediction');
    }
    return res.json();
  },

  // Multi-Merchant Portal
  listMerchants: async () => {
    const res = await fetch(`${API_BASE}/merchants`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch merchants');
    return res.json();
  },

  getMerchant: async (merchantId: string) => {
    const res = await fetch(`${API_BASE}/merchants/${merchantId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch merchant details');
    return res.json();
  },

  uploadMerchantPolicy: async (merchantId: string, data: {
    title: string;
    policy_type?: string;
    content: string;
    rules?: Record<string, any>;
  }) => {
    const res = await fetch(`${API_BASE}/merchants/${merchantId}/policies`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload policy');
    }
    return res.json();
  },

  simulatePolicy: async (merchantId: string, data: {
    transaction_amount: number;
    issue_type: string;
    transaction_age_days: number;
    evidence_provided: boolean;
    custom_rules?: Record<string, any>;
  }) => {
    const res = await fetch(`${API_BASE}/merchants/${merchantId}/simulate-policy`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to simulate policy');
    }
    return res.json();
  },

  // Notifications
  getNotifications: async () => {
    const res = await fetch(`${API_BASE}/notifications`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  markNotificationAsRead: async (id: string) => {
    const res = await fetch(`${API_BASE}/notifications/${id}/read`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to mark notification as read');
    return res.json();
  }
};
