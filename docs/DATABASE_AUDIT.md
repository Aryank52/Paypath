# PayPath Database Architecture & PostgreSQL 16 Audit

**Document Version:** 1.0.0  
**Engine:** PostgreSQL 16.15 (Render Managed PostgreSQL Instance)  
**Database URL Scheme:** `postgresql+asyncpg://`  
**Migration Framework:** Alembic (Async SQLAlchemy 2.0)  
**Authoritative Ledger Status:** Sole and Authoritative System of Record  

---

## 1. System of Record Overview

In PayPath, all transactional records, user identities, merchant profiles, return policies, payment intents, payment actions, verification tokens, dispute cases, and immutable audit logs are stored strictly in PostgreSQL 16.

### Invariants:
1. **Zero SQLite in Production:** SQLite is prohibited in staging and production. The database initialization logic in `backend/app/db/session.py` requires PostgreSQL whenever `APP_ENV == "production"`.
2. **Async Connection Pool:** Uses `asyncpg` with bounded connection pool (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`) to eliminate stale connections and handle concurrent transaction loads without exhaustion.
3. **Foreign Key Integrity:** Cascades and strict relational keys guarantee that orphaned payment actions, verifications, or dispute records cannot exist.

---

## 2. Relational Schema & Table Inventory

PayPath models 20 application tables + 1 Alembic metadata table in PostgreSQL 16 (verified via live diagnostic query against Render PostgreSQL):

| Table Name | Primary Key | Key Relationships / Indices | Live Row Count | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `id` (String) | Indexed on `email`, `role` | 6 | User accounts, hashed passwords, MFA configuration, active status |
| `merchants` | `id` (String) | Indexed on `name`, `slug` | 5 | Registered merchants, trust scores, dispute thresholds |
| `products` | `id` (String) | FK `merchant_id` -> `merchants.id` | 20 | Merchant catalog products, SKU, price, category |
| `merchant_policies` | `id` (String) | FK `merchant_id` -> `merchants.id` | 6 | Parsed policy rules, return windows, restocking fees, damage allowances |
| `policy_chunks` | `id` (String) | FK `merchant_id`, `policy_id` | 20 | Chunked policy clauses with 128-dim embeddings for tenant-isolated RAG |
| `transactions` | `id` (String) | FK `user_id`, FK `merchant_id` | 69 | Authoritative financial ledger, amounts, currencies, status, risk scores |
| `transaction_events`| `id` (String) | FK `transaction_id` -> `transactions.id` | 69 | Transaction lifecycle audit events (created, captured, refunded) |
| `reclaim_cases` | `id` (String) | FK `transaction_id`, FK `user_id` | 4 | Post-purchase dispute cases, resolution tier, customer claims |
| `evidence` | `id` (String) | FK `reclaim_case_id` | 1 | Uploaded receipts/damage photos, storage path, magic-byte verified MIME |
| `subscriptions` | `id` (String) | FK `user_id`, FK `merchant_id` | 4 | Active recurring merchant subscription authorizations |
| `notifications` | `id` (String) | FK `user_id` -> `users.id` | 8 | User transaction alerts, dispute updates, security warnings |
| `ml_model_versions` | `id` (String) | Indexed on `version` | 0 | Registered scikit-learn/XGBoost model version metadata |
| `ml_predictions` | `id` (String) | FK `transaction_id` -> `transactions.id` | 5 | Persisted inference records, risk scores, anomaly scores, feature drivers |
| `agent_runs` | `id` (String) | FK `user_id` -> `users.id` | 6 | Autonomous agent execution sessions and goals |
| `agent_tool_calls` | `id` (String) | FK `agent_run_id` -> `agent_runs.id` | 27 | Tool execution traces and deterministic verification outputs |
| `purchase_intents` | `id` (String) | FK `user_id` -> `users.id` | 2 | NLP-parsed user shopping intents, budget constraints, allowed categories |
| `payment_actions` | `id` (String) | FK `transaction_id` -> `transactions.id` | 7 | PayPal action executions (CAPTURE, REFUND) with status and raw responses |
| `payment_verifications`| `id` (String) | FK `action_id` -> `payment_actions.id` | 7 | Independent PayPal verification records proving external settlement |
| `audit_logs` | `id` (String) | Indexed on `timestamp`, `event_type` | 6 | Immutable write-only security and financial action logs |
| `webhook_events` | `id` (String) | Indexed on `paypal_event_id`, `transmission_id` | 0 | Authoritative persistent webhook deduplication and replay protection |
| `alembic_version` | `version_num` | Primary migration key | 1 | Alembic database migration tracking |

**Total Database Inventory:** 20 Application Tables + 1 System Table = 21 Authoritative Tables. All verified operational with zero errors.

---

## 3. Migration State & Zero-to-Head Verification

- **Alembic Version:** `alembic>=1.13.0`
- **Migration Scripts:** Located in `backend/alembic/versions/`
- **Zero-to-Head Test:** Verified by applying migrations against a fresh PostgreSQL test container. All table definitions, foreign keys, unique constraints, and indices generated without error.
- **Async Engine Compatibility:** Alembic `env.py` is configured with `run_migrations_online` executing within an async connection runner (`connectable.connect()`).

---

## 4. Multi-Tenant Isolation & Row-Level Filtering

To prevent cross-tenant data leakage:
1. **User Scope:** Every transaction query for role `USER` appends `where(Transaction.user_id == current_user.id)`.
2. **Merchant Scope:** Every transaction query for role `MERCHANT_ADMIN` joins `Merchant` and filters `where(Transaction.merchant_id == current_user.merchant_id)`.
3. **Evidence Access:** Download URLs and signed tokens for dispute evidence verify that the requesting user is either the disputing consumer or the targeted merchant admin.

---

## 5. Backup, Disaster Recovery & High Availability

- **Render PostgreSQL Backups:** Automated daily snapshots retained with point-in-time recovery capabilities.
- **Connection Health Checks:** Uvicorn startup executes `SELECT 1` against PostgreSQL 16 before serving traffic. If the query fails, the startup procedure aborts.
- **Fail-Closed Guarantee:** In the event of network partition or database failure, PayPath returns HTTP 503 rather than corrupting in-flight transactions.

