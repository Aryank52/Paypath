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
- **Backend Test Suite:** 53 tests passing in `backend/tests/` (100% pass rate in 67s):
  - `test_adversarial_deep.py` (6 tests): Auth session token revocation, TOTP MFA lifecycle, password reset replay defense, IDOR transaction access prevention, RBAC merchant operations denial, financial refund invariants.
  - `test_agents.py` (4 tests): IntentAgent extraction, ShoppingAgent catalog recommendations, EvidenceAgent analysis, ResolutionAgent settlement proposal.
  - `test_api_endpoints.py` (5 tests): Health check, transactions list, intent parsing, spend guard evaluation, agent commerce workflow.
  - `test_mfa_and_upload_security.py` (3 tests): MFA lifecycle, password reset security, binary magic-byte inspection.
  - `test_ml_pipeline.py` (5 tests): Deterministic feature extraction & leakage exclusion, temporal split integrity, XGBoost risk & Isolation Forest training & PostgreSQL registry persistence, real-time explainability & advisory safety contract, API endpoints (`/api/v1/ml/*`).
  - `test_paycore_reclaim.py` (1 test): Complete PayCore and RECLAIM lifecycle.
  - `test_paypal_webhook_security.py` (11 tests): Missing headers, SSRF cert URL validation, timestamp replay defense, RSA signature verification, payload modification rejection, missing event ID rejection, valid event ingestion & deduplication, duplicate transmission ID handling, unknown event handling, capture reconciliation mismatch.
  - `test_paypath_end_to_end_integration.py` (2 tests): End-to-end Agentic Commerce lifecycle (Intent -> Search -> Guard -> Order -> Capture -> Verification -> ML Scoring) and end-to-end RECLAIM dispute & refund lifecycle (Dispute -> RAG Policy -> Multi-Agent Consensus -> Human Approval -> Refund Mutation -> Verification).
  - `test_policy_engine.py` (6 tests): Spend caps, user intent budgets, restricted categories, return windows, damage coverage, and refund limits.
  - `test_security_and_edge_cases.py` (7 tests): Prompt injection defense, refund boundary checks, idempotent refund replay, webhook deduplication, ML explain IDOR protection, administrative endpoints RBAC enforcement (`/audit`, `/system/database`), policy upload RBAC enforcement (`/policies/upload`).
  - `test_system_health_and_database.py` (3 tests): Multi-subsystem health aggregation endpoint, database table inventory inspection, seed idempotency across repeated runs.
- **Frontend Production Build:** React 19 + TypeScript + Vite. Vite build succeeded with 0 errors in 4.09s (`dist/assets/index-*.js`, `dist/assets/index-*.css`). Premium Fintech Minimalism + Bento Grid styling verified. DPDP Act 2023 modal, Grievance Officer disclosures (`grievance@paypath.finance`), and RECLAIM refund disclosures integrated.
- **Audit Documentation Suite (Master Phase 24):**
  - `docs/API_TRACE_MATRIX.md`: 30 end-to-end interactions traced across UI -> API -> Service -> DB -> AI/ML -> PayPal -> User Feedback.
  - `docs/FEATURE_COMPLETENESS_AUDIT.md`: 22/22 features operational with 0 mocks and 0 orphan routes.
  - `docs/UI_UX_AUDIT.md`: Certified removal of all AI-slop; WCAG 2.2 AA contrast verified.
  - `docs/PAYPAL_CAPABILITY_AUDIT.md`: 12 PayPal REST capabilities evaluated; public webhook registration deferral policy confirmed.
  - `docs/RAG_EVALUATION.md`: 7 real-world dispute benchmarks evaluated with 0.8391 mean cosine similarity and 100% citation accuracy.
  - `docs/SECURITY_REAUDIT.md`: 78 baseline controls + 4 Gate A controls verified; 0 high/critical vulnerabilities.
  - `docs/PRODUCTION_FUNCTIONAL_AUDIT.md`: 8 user journeys verified with empirical latencies and 21 database tables.
- **Live Localhost Connectivity Verified:**
  - PostgreSQL 16.15: Running on port 5432 (`CONNECTED`).
  - FastAPI ASGI Uvicorn server: Running on port 8000 (`HEALTHY`).
  - Vite Dev server: Running on port 5173 (`HEALTHY`).
- **PostgreSQL 16 Authoritative State:**
  - 21 public tables verified; 305+ transactions, 140+ audit logs, 19 RAG vectorized clauses persisted.

## 3. Key Design Conventions
- **Dual-Phase Read-Back Verification:** Mutating actions (`capture_order`, `execute_refund`) query PayPal directly post-mutation to compare actual vs. expected amount, currency, and completion status.
- **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries feed into the deterministic `PolicyEngine`. AI and ML models emit advisory scores and do not possess final authorization authority.
- **Idempotency Protection:** Every financial mutation enforces unique idempotency keys (`payment_actions.idempotency_key`), preventing duplicate transactions or duplicate refunds.
- **Tenant Isolation:** Multi-tenancy strictly enforced via `merchant_id` across databases, policies, and vector similarity retrieval.
- **Security Hardening:** Base32 TOTP MFA, SHA-256 password reset tokens, binary magic-byte inspection (JPEG, PNG, WEBP, PDF), and 10MB upload ceiling.
