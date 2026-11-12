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

PayPath models 14 core tables in PostgreSQL:

| Table Name | Primary Key | Key Relationships / Indices | Purpose |
| :--- | :--- | :--- | :--- |
| `users` | `id` (UUID) | Indexed on `email`, `role` | User accounts, hashed passwords, MFA configuration, active status |
| `merchants` | `id` (UUID) | Indexed on `name`, `paypal_merchant_id` | Registered merchants, trust scores, dispute thresholds |
| `merchant_policies` | `id` (UUID) | FK `merchant_id` -> `merchants.id` | Parsed policy rules, return windows, restocking fees, damage allowances |
| `transactions` | `id` (UUID) | FK `user_id` -> `users.id`, FK `merchant_id` -> `merchants.id` | Authoritative financial ledger, amounts, currencies, status, risk scores |
| `user_intents` | `id` (UUID) | FK `user_id` -> `users.id` | NLP-parsed user shopping intents, budget constraints, allowed categories |
| `payment_actions` | `id` (UUID) | FK `transaction_id` -> `transactions.id` | PayPal action executions (CAPTURE, REFUND, AUTHORIZE, VOID) with status and raw responses |
| `action_verifications` | `id` (UUID) | FK `action_id` -> `payment_actions.id` | Independent PayPal verification records proving external settlement |
| `reclaim_cases` | `id` (UUID) | FK `transaction_id` -> `transactions.id`, FK `user_id` -> `users.id` | Post-purchase dispute cases, resolution tier, customer claims |
| `reclaim_evidence` | `id` (UUID) | FK `case_id` -> `reclaim_cases.id` | Uploaded receipts/damage photos, Supabase storage path, magic-byte verified MIME |
| `reclaim_events` | `id` (UUID) | FK `case_id` -> `reclaim_cases.id` | Dispute audit timeline, status changes, settlement amounts |
| `notifications` | `id` (UUID) | FK `user_id` -> `users.id` | User transaction alerts, dispute updates, security warnings |
| `token_revocations` | `jti` (String) | Indexed on `jti`, `expires_at` | Blocklist of logged-out JWT tokens |
| `audit_logs` | `id` (UUID) | Indexed on `timestamp`, `event_type` | Immutable write-only security and financial action logs |
| `ml_model_metadata` | `model_name` (String) | Indexed on `version` | Registered scikit-learn/XGBoost model metrics, weights, and training timestamps |

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
