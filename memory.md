# PayPath — Project Memory

## 1. Environment & Infrastructure Knowledge
- **Host OS:** Windows 11 (64-bit).
- **Runtimes:**
  - Python 3.12.10 (virtual environment active at `.venv/`)
  - Node.js v24.16.0 & npm 11.13.0
  - PostgreSQL 16.15 service running authoritative on `127.0.0.1:5432`, database `paypath`.
  - Machine Learning packages: `scikit-learn 1.9.1`, `xgboost 3.4.1`, `pandas 3.1.1`.
  - Git repository on `main` branch.

## 2. Tested & Verified Capabilities
- **Backend Test Suite:** 39 tests passing in `backend/tests/` (100% pass rate):
  - `test_adversarial_deep.py` (6 tests): Auth session token revocation, TOTP MFA lifecycle, password reset replay defense, IDOR transaction access prevention, RBAC merchant operations denial, financial refund invariants.
  - `test_agents.py` (4 tests): IntentAgent extraction, ShoppingAgent catalog recommendations, EvidenceAgent analysis, ResolutionAgent settlement proposal.
  - `test_api_endpoints.py` (5 tests): Health check, transactions list, intent parsing, spend guard evaluation, agent commerce workflow.
  - `test_mfa_and_upload_security.py` (3 tests): MFA lifecycle, password reset security, binary magic-byte inspection.
  - `test_ml_pipeline.py` (5 tests): Deterministic feature extraction & leakage exclusion, temporal split integrity, XGBoost risk & Isolation Forest training & PostgreSQL registry persistence, real-time explainability & advisory safety contract, API endpoints (`/api/v1/ml/*`).
  - `test_paycore_reclaim.py` (1 test): Complete PayCore and RECLAIM lifecycle.
  - `test_paypath_end_to_end_integration.py` (2 tests): End-to-end Agentic Commerce lifecycle (Intent -> Search -> Guard -> Order -> Capture -> Verification -> ML Scoring) and end-to-end RECLAIM dispute & refund lifecycle (Dispute -> RAG Policy -> Multi-Agent Consensus -> Human Approval -> Refund Mutation -> Verification).
  - `test_policy_engine.py` (6 tests): Spend caps, user intent budgets, restricted categories, return windows, damage coverage, and refund limits.
  - `test_security_and_edge_cases.py` (4 tests): Prompt injection defense, refund boundary checks, idempotent refund replay, webhook deduplication.
  - `test_system_health_and_database.py` (3 tests): Multi-subsystem health aggregation endpoint, database table inventory inspection, seed idempotency across repeated runs.
- **Frontend Production Build:** Vite build succeeded with 0 errors in 3.87s (`dist/assets/index-*.js`, `dist/assets/index-*.css`).
- **Live Localhost Connectivity Verified:**
  - FastAPI ASGI Uvicorn server: Running on `http://127.0.0.1:8000` (PID 29172). Health endpoint reports `{"status": "HEALTHY", "database": "PostgreSQL 16", "database_status": "CONNECTED"}`.
  - Vite Dev server: Running on `http://127.0.0.1:5173`.
  - Reverse Proxy: Tested and verified `http://127.0.0.1:5173/api/v1/transactions` successfully returns seeded PostgreSQL transactions.
- **Comprehensive PostgreSQL Seed:**
  - 5 users, 5 merchants, 20 products, 5 structured policies with RAG chunks and vector embeddings, 68 transactions, 66 timeline events, 4 RECLAIM cases, 1 evidence record, 4 subscriptions, 8 notifications, 12 ML model versions, 5 ML predictions, 1 agent run, 3 tool calls.
- **Documentation Suite:** Complete specifications in `docs/` (`ML_PIPELINE.md`, `DATA_ARCHITECTURE.md`, `SYSTEM_INTEGRATION.md`, `SEED_DATA.md`, `PRD.md`, `TRD.md`, `FLOW.md`, `BACKEND_SCHEMA.md`, `API_SPEC.md`).

## 3. Key Design Conventions
- **Dual-Phase Read-Back Verification:** Mutating actions (`capture_order`, `execute_refund`) query PayPal directly post-mutation to compare actual vs. expected amount, currency, and completion status.
- **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries feed into the deterministic `PolicyEngine`. AI and ML models emit advisory scores and do not possess final authorization authority.
- **Idempotency Protection:** Every financial mutation enforces unique idempotency keys (`payment_actions.idempotency_key`), preventing duplicate transactions or duplicate refunds.
- **Tenant Isolation:** Multi-tenancy strictly enforced via `merchant_id` across databases, policies, and vector similarity retrieval.
- **Security Hardening:** Base32 TOTP MFA, SHA-256 password reset tokens, binary magic-byte inspection (JPEG, PNG, WEBP, PDF), and 10MB upload ceiling.
