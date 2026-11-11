export interface TransactionEvent {
  id: string;
  event_type: string;
  actor: string;
  description: string;
  payload?: any;
  created_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  merchant_id?: string;
  merchant_name: string;
  paypal_order_id?: string;
  paypal_capture_id?: string;
  amount: number;
  currency: string;
  status: 'CREATED' | 'CAPTURED' | 'REFUNDED' | 'PARTIALLY_REFUNDED' | 'FAILED' | 'DISPUTED';
  verification_status: 'PENDING' | 'VERIFIED' | 'MISMATCH' | 'FAILED';
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  ai_summary?: string;
  item_description?: string;
  created_at: string;
  events?: TransactionEvent[];
}

export interface EvidenceItem {
  evidence_id: string;
  file_name: string;
  file_url: string;
  evidence_type: string;
  confidence_score: number;
  analysis_summary: string;
}

export interface ReclaimCase {
  id: string;
  transaction_id: string;
  user_id: string;
  issue_type: 'DAMAGED_ITEM' | 'WRONG_ITEM' | 'NOT_RECEIVED' | 'DUPLICATE_CHARGE';
  description: string;
  status: 'OPEN' | 'EVIDENCE_REQUIRED' | 'UNDER_REVIEW' | 'AI_RECOMMENDED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'RESOLVED' | 'REJECTED';
  proposed_resolution?: 'FULL_REFUND' | 'PARTIAL_REFUND' | 'REPLACEMENT' | 'NO_ACTION' | 'ESCALATE';
  recommended_amount?: number;
  confidence_score?: number;
  ai_reasoning?: string;
  policy_citation?: {
    merchant_name: string;
    policy_title: string;
    section: string;
    excerpt: string;
    applicability: string;
    rules?: any;
  };
  approval_status: 'PENDING' | 'USER_APPROVED' | 'MERCHANT_APPROVED' | 'REJECTED';
  created_at: string;
  evidence_items?: EvidenceItem[];
}

export interface Product {
  id: string;
  title: string;
  category: string;
  price: number;
  currency: string;
  merchant_name: string;
  rating: number;
  features: string[];
  in_stock: boolean;
  image_url: string;
  matches_budget?: boolean;
  ai_recommendation_score?: number;
  recommendation_rationale?: string;
}

export interface GuardEvaluation {
  decision: 'ALLOW' | 'REVIEW' | 'BLOCK' | 'ESCALATE';
  is_allowed: boolean;
  requires_approval: boolean;
  reason: string;
  risk_score: number;
  applied_rules: string[];
  max_budget?: number;
  requested_amount: number;
}

export interface AgentTraceStep {
  step_id?: string;
  agent_name: string;
  role: string;
  action: string;
  summary: string;
  status: 'COMPLETED' | 'RUNNING' | 'FAILED';
  details?: any;
  timestamp: string;
}

export interface SubscriptionItem {
  id: string;
  merchant_name: string;
  amount: number;
  currency: string;
  billing_interval: string;
  last_payment_date?: string;
  next_expected_date?: string;
  status: string;
}

export interface DuplicateSignal {
  original_transaction_id: string;
  duplicate_transaction_id: string;
  merchant_name: string;
  amount: number;
  currency: string;
  confidence_score: number;
  signal_type: string;
  explanation: string;
  recommended_action: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  mobile_number?: string;
  preferred_currency: string;
  role: 'USER' | 'MERCHANT_USER' | 'MERCHANT_ADMIN' | 'PLATFORM_ADMIN';
  is_active: boolean;
  email_verified: boolean;
  mfa_enabled: boolean;
}


