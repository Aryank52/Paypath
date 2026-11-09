import {
  Transaction,
  TransactionEvent,
  ReclaimCase,
  EvidenceItem,
  Product,
  GuardEvaluation,
  AgentTraceStep,
  SubscriptionItem,
  DuplicateSignal
} from '../types';

const API_BASE = '/api/v1';

export const api = {
  // Transactions
  getTransactions: async (params?: { status?: string; risk_level?: string; merchant_name?: string }): Promise<Transaction[]> => {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.risk_level) query.append('risk_level', params.risk_level);
    if (params?.merchant_name) query.append('merchant_name', params.merchant_name);
    const res = await fetch(`${API_BASE}/transactions?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch transactions');
    return res.json();
  },

  getTransaction: async (id: string): Promise<Transaction> => {
    const res = await fetch(`${API_BASE}/transactions/${id}`);
    if (!res.ok) throw new Error('Failed to fetch transaction details');
    return res.json();
  },

  getTransactionEvents: async (id: string): Promise<TransactionEvent[]> => {
    const res = await fetch(`${API_BASE}/transactions/${id}/events`);
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create order');
    return res.json();
  },

  captureOrder: async (orderId: string) => {
    const res = await fetch(`${API_BASE}/paycore/orders/capture`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId })
    });
    if (!res.ok) throw new Error('Failed to capture order');
    return res.json();
  },

  refundPayment: async (data: { transaction_id: string; amount: number; reason?: string }) => {
    const res = await fetch(`${API_BASE}/paycore/refunds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to execute refund');
    return res.json();
  },

  verifyResource: async (resourceId: string, actionType: 'CAPTURE' | 'REFUND' = 'CAPTURE', expectedAmount = 89.0) => {
    const res = await fetch(`${API_BASE}/paycore/verify/${resourceId}?action_type=${actionType}&expected_amount=${expectedAmount}`);
    if (!res.ok) throw new Error('Failed to verify resource');
    return res.json();
  },

  // Shopping & Intent
  parseIntent: async (prompt: string) => {
    const res = await fetch(`${API_BASE}/intent/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) throw new Error('Failed to parse intent');
    return res.json();
  },

  searchProducts: async (category = 'headphones', budget = 100.0, purpose = 'travel'): Promise<Product[]> => {
    const res = await fetch(`${API_BASE}/shop/search?category=${encodeURIComponent(category)}&budget=${budget}&purpose=${encodeURIComponent(purpose)}`);
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to evaluate purchase proposal');
    return res.json();
  },

  // Payment Guard
  evaluateGuard: async (data: { amount: number; merchant_name: string; category?: string }): Promise<GuardEvaluation> => {
    const res = await fetch(`${API_BASE}/guard/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to evaluate guard');
    return res.json();
  },

  // RECLAIM
  createReclaimCase: async (data: { transaction_id: string; issue_type: string; description: string }): Promise<ReclaimCase> => {
    const res = await fetch(`${API_BASE}/reclaim/cases`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create dispute case');
    return res.json();
  },

  uploadEvidence: async (caseId: string, file: File): Promise<EvidenceItem> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/evidence`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload evidence');
    return res.json();
  },

  evaluateCase: async (caseId: string) => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/evaluate`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to evaluate dispute case');
    return res.json();
  },

  approveRefund: async (caseId: string) => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}/approve`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to approve and execute refund');
    return res.json();
  },

  getCase: async (caseId: string): Promise<ReclaimCase> => {
    const res = await fetch(`${API_BASE}/reclaim/cases/${caseId}`);
    if (!res.ok) throw new Error('Failed to get dispute case');
    return res.json();
  },

  // Recovery Intelligence
  getDuplicates: async (): Promise<DuplicateSignal[]> => {
    const res = await fetch(`${API_BASE}/recover/duplicates`);
    if (!res.ok) throw new Error('Failed to fetch duplicate signals');
    return res.json();
  },

  getSubscriptions: async (): Promise<SubscriptionItem[]> => {
    const res = await fetch(`${API_BASE}/recover/subscriptions`);
    if (!res.ok) throw new Error('Failed to fetch subscriptions');
    return res.json();
  },

  // Agents
  runCommerceWorkflow: async (prompt: string) => {
    const res = await fetch(`${API_BASE}/agents/run-commerce`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) throw new Error('Failed to run commerce workflow');
    return res.json();
  },

  runReclaimWorkflow: async (data: any) => {
    const res = await fetch(`${API_BASE}/agents/run-reclaim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to run reclaim workflow');
    return res.json();
  },

  // Audit
  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/audit`);
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
    const res = await fetch(`${API_BASE}/system/database`);
    if (!res.ok) throw new Error('Failed to fetch database inventory');
    return res.json();
  },

  // Machine Learning
  getMLModels: async () => {
    const res = await fetch(`${API_BASE}/ml/models`);
    if (!res.ok) throw new Error('Failed to fetch ML models');
    return res.json();
  },

  getMLFeatures: async () => {
    const res = await fetch(`${API_BASE}/ml/features`);
    if (!res.ok) throw new Error('Failed to fetch ML features');
    return res.json();
  },

  explainTransaction: async (id: string) => {
    const res = await fetch(`${API_BASE}/ml/explain/${id}`);
    if (!res.ok) throw new Error('Failed to explain transaction');
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to run ML prediction');
    return res.json();
  }
};

