# PayPath Privacy & Financial Data Protection Specification

## Core Privacy Architecture
PayPath is engineered around privacy-by-design for high-sensitivity fintech data.

### 1. Zero Payment Credential Ingestion
- PayPath **never** receives, parses, stores, or logs raw credit card numbers, CVVs, debit card PINs, or bank account credentials.
- All monetary transactions are tokenized and processed through PayPal's secure checkout infrastructure.
- PayPath handles only PayPal Order IDs, Capture IDs, and tokenized authorization references.

### 2. Tenant Isolation in RAG & Vector Retrieval
- All vector search queries enforce strict multi-tenant boundaries using `merchant_id` filters.
- A merchant's proprietary warranty, damage tolerance, or return policies are strictly segregated and cannot leak to competitors or external shoppers.

### 3. PII Minimization in AI Inference
- When prompts are sent to LLM providers (e.g., Gemini), personally identifiable information (PII) is redacted or minimized:
  - Email addresses, physical street addresses, and full credit cardholder identities are stripped from prompts.
  - LLMs receive only the normalized item description, claim issue category, and extracted policy terms.

### 4. Data Retention & Erasure (GDPR / CCPA)
- Users may request complete erasure of their account data.
- Deletion cascades across `users`, `purchase_intents`, and `subscriptions`.
- Financial transaction IDs and audit logs are retained in pseudonymized form for regulatory compliance and fraud prevention.

