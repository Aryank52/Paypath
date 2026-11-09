# PayPath — Backend Database Schema Specification

## 1. Overview & Technology
- **Engine:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (Async) + Pydantic v2
- **Vector Search:** `pgvector` extension for policy chunk embeddings (`vector(768)` or `vector(1536)`).
- **Primary Keys:** UUID v4 across all tables for secure reference.
- **Audit Standard:** Append-only logs, immutable transaction events, soft delete support where applicable.

---

## 2. Table Schemata

### `users`
- `id` (UUID, PK)
- `email` (VARCHAR(255), UNIQUE, NOT NULL)
- `hashed_password` (VARCHAR(255), NOT NULL)
- `full_name` (VARCHAR(255))
- `role` (ENUM: 'USER', 'MERCHANT_USER', 'MERCHANT_ADMIN', 'PLATFORM_ADMIN')
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `merchants`
- `id` (UUID, PK)
- `name` (VARCHAR(255), NOT NULL)
- `slug` (VARCHAR(100), UNIQUE, NOT NULL)
- `paypal_merchant_id` (VARCHAR(100))
- `support_email` (VARCHAR(255))
- `is_verified` (BOOLEAN, DEFAULT FALSE)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `merchant_policies`
- `id` (UUID, PK)
- `merchant_id` (UUID, FK -> merchants.id, NOT NULL)
- `title` (VARCHAR(255), NOT NULL)
- `policy_type` (ENUM: 'REFUND', 'RETURN', 'WARRANTY', 'SPENDING')
- `raw_content` (TEXT, NOT NULL)
- `status` (ENUM: 'DRAFT', 'PUBLISHED', 'ARCHIVED')
- `version` (INTEGER, DEFAULT 1)
- `rules_json` (JSONB)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `policy_chunks`
- `id` (UUID, PK)
- `policy_id` (UUID, FK -> merchant_policies.id, NOT NULL)
- `merchant_id` (UUID, FK -> merchants.id, NOT NULL)
- `section_title` (VARCHAR(255))
- `content` (TEXT, NOT NULL)
- `metadata` (JSONB)
- `embedding` (VECTOR(768)) -- fallback to JSON or text if vector disabled
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())

### `purchase_intents`
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id, NOT NULL)
- `raw_prompt` (TEXT, NOT NULL)
- `category` (VARCHAR(100))
- `purpose` (VARCHAR(255))
- `budget_amount` (NUMERIC(12, 2))
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `approval_required` (BOOLEAN, DEFAULT TRUE)
- `autonomy_level` (ENUM: 'RESTRICTED', 'SUPERVISED', 'AUTONOMOUS')
- `status` (ENUM: 'ACTIVE', 'FULFILLED', 'EXPIRED', 'CANCELLED')
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())

### `transactions`
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id, NOT NULL)
- `merchant_id` (UUID, FK -> merchants.id, NULLABLE)
- `paypal_order_id` (VARCHAR(100), INDEX)
- `paypal_capture_id` (VARCHAR(100), INDEX)
- `amount` (NUMERIC(12, 2), NOT NULL)
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `status` (ENUM: 'CREATED', 'CAPTURED', 'REFUNDED', 'PARTIALLY_REFUNDED', 'FAILED', 'DISPUTED')
- `verification_status` (ENUM: 'PENDING', 'VERIFIED', 'MISMATCH', 'FAILED')
- `risk_score` (NUMERIC(4, 2), DEFAULT 0.0) -- 0.0 to 1.0
- `risk_level` (ENUM: 'LOW', 'MEDIUM', 'HIGH')
- `ai_summary` (TEXT)
- `item_description` (TEXT)
- `metadata` (JSONB)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `transaction_events`
- `id` (UUID, PK)
- `transaction_id` (UUID, FK -> transactions.id, NOT NULL)
- `event_type` (VARCHAR(100), NOT NULL)
- `actor` (VARCHAR(100), NOT NULL) -- 'SYSTEM', 'USER', 'PAYPAL', 'AGENT'
- `description` (TEXT, NOT NULL)
- `payload` (JSONB)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())

### `payment_actions`
- `id` (UUID, PK)
- `transaction_id` (UUID, FK -> transactions.id, NOT NULL)
- `action_type` (ENUM: 'CAPTURE', 'REFUND', 'AUTHORIZE')
- `requested_amount` (NUMERIC(12, 2), NOT NULL)
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `idempotency_key` (VARCHAR(255), UNIQUE, NOT NULL)
- `state` (ENUM: 'PROPOSED', 'AWAITING_APPROVAL', 'APPROVED', 'EXECUTING', 'EXECUTED', 'VERIFIED', 'FAILED', 'REJECTED')
- `paypal_reference_id` (VARCHAR(100))
- `error_message` (TEXT)
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `payment_verifications`
- `id` (UUID, PK)
- `payment_action_id` (UUID, FK -> payment_actions.id, NOT NULL)
- `paypal_resource_id` (VARCHAR(100), NOT NULL)
- `expected_amount` (NUMERIC(12, 2), NOT NULL)
- `actual_amount` (NUMERIC(12, 2), NOT NULL)
- `expected_currency` (VARCHAR(3), NOT NULL)
- `actual_currency` (VARCHAR(3), NOT NULL)
- `is_verified` (BOOLEAN, NOT NULL)
- `verification_details` (JSONB)
- `verified_at` (TIMESTAMPTZ, DEFAULT NOW())

### `reclaim_cases` (Resolutions)
- `id` (UUID, PK)
- `transaction_id` (UUID, FK -> transactions.id, NOT NULL)
- `user_id` (UUID, FK -> users.id, NOT NULL)
- `issue_type` (ENUM: 'DAMAGED_ITEM', 'WRONG_ITEM', 'NOT_RECEIVED', 'DUPLICATE_CHARGE', 'CANCELLED_SERVICE')
- `description` (TEXT, NOT NULL)
- `status` (ENUM: 'OPEN', 'EVIDENCE_REQUIRED', 'UNDER_REVIEW', 'AI_RECOMMENDED', 'AWAITING_APPROVAL', 'APPROVED', 'RESOLVED', 'REJECTED')
- `proposed_resolution` (ENUM: 'FULL_REFUND', 'PARTIAL_REFUND', 'REPLACEMENT', 'NO_ACTION', 'ESCALATE')
- `recommended_amount` (NUMERIC(12, 2))
- `confidence_score` (NUMERIC(4, 2)) -- 0.00 to 1.00
- `ai_reasoning` (TEXT)
- `policy_citation` (JSONB)
- `approval_status` (ENUM: 'PENDING', 'USER_APPROVED', 'MERCHANT_APPROVED', 'REJECTED')
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ, DEFAULT NOW())

### `evidence`
- `id` (UUID, PK)
- `reclaim_case_id` (UUID, FK -> reclaim_cases.id, NOT NULL)
- `file_name` (VARCHAR(255), NOT NULL)
- `file_type` (VARCHAR(100), NOT NULL)
- `file_url` (VARCHAR(500), NOT NULL)
- `evidence_type` (ENUM: 'PHOTO_DAMAGE', 'INVOICE', 'CORRESPONDENCE', 'TRACKING_PROOF')
- `analysis_summary` (TEXT)
- `confidence_score` (NUMERIC(4, 2))
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())

### `audit_logs`
- `id` (UUID, PK)
- `action` (VARCHAR(100), NOT NULL)
- `actor_type` (VARCHAR(50), NOT NULL) -- 'USER', 'AGENT', 'SYSTEM'
- `actor_id` (VARCHAR(100))
- `resource_type` (VARCHAR(100), NOT NULL)
- `resource_id` (VARCHAR(100), NOT NULL)
- `details` (JSONB)
- `ip_address` (VARCHAR(50))
- `created_at` (TIMESTAMPTZ, DEFAULT NOW())

