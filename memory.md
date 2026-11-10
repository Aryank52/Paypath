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
- **Frontend Production Build:** React 19.3.1 + Vite 8.3.6. Vite build succeeded with 0 errors in 5.03s (`dist/assets/index-*.js`, `dist/assets/index-*.css`). Live Provider Status Matrix and ML Benchmark validation disclosures integrated into `SystemIntelligenceView.tsx`.
- **Live Localhost Connectivity Verified:**
  - FastAPI ASGI Uvicorn server: Running on `http://127.0.0.1:8000`. Health endpoint reports multi-subsystem states (`postgresql: healthy`, `paypal: not_configured`, `llm: mock`, `rag: healthy`, `ml: validated`, `agents: healthy`, `frontend: healthy`, `redis: not_configured`, `storage: healthy`, `notifications: healthy`).
  - Vite Dev server: Running on `http://127.0.0.1:5173`.
  - Reverse Proxy: Tested and verified `http://127.0.0.1:5173/api/v1/transactions` successfully returns seeded PostgreSQL transactions.
- **PostgreSQL 16 Authoritative State:**
  - Exact 20 tables in public schema, 238 baseline records populated via idempotent seeder, 304 total live records verified in PostgreSQL post-certification (including 7 agent runs and 30 agent tool calls).
- **Provider Multi-State Lifecycle Telemetry:**
  - `llm_provider.py` and `client.py` report truth states (`NOT_CONFIGURED`, `MOCK`, `CONFIGURED`, `CONNECTED`, `ERROR`) instead of collapsed booleans.
- **Verified Financial Safety & Invariant Replay:**
  - `backend/scripts/test_paypal_invariants.py`: Verified order creation, capture, partial refund, exact replay idempotency, 409 Conflict on altered replay amounts, and 400 rejection on exceeding balance.
- **Verified RAG Isolation & Grounded Citation:**
  - `backend/scripts/test_rag_isolation.py`: Cosine similarity retrieval with 0 cross-merchant clause leaks across isolated tenants.
- **Agent Trace Persistence:**
  - `orchestrator.py` persists execution traces directly to PostgreSQL `agent_runs` and `agent_tool_calls` tables for both commerce and dispute recovery workflows.
- **Documentation Suite:** Fully reconciled across `docs/FINAL_STATE_RECONCILIATION.md`, `docs/PROVIDER_STATUS.md`, `docs/RELEASE.md`, `docs/AGENT_SPEC.md`, `docs/DATA_ARCHITECTURE.md`, `docs/PRE_RELEASE_AUDIT.md`, `docs/GAP_ANALYSIS.md`, and `architecture.md`.

## 3. Key Design Conventions
- **Dual-Phase Read-Back Verification:** Mutating actions (`capture_order`, `execute_refund`) query PayPal directly post-mutation to compare actual vs. expected amount, currency, and completion status.
- **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries feed into the deterministic `PolicyEngine`. AI and ML models emit advisory scores and do not possess final authorization authority.
- **Idempotency Protection:** Every financial mutation enforces unique idempotency keys (`payment_actions.idempotency_key`), preventing duplicate transactions or duplicate refunds.
- **Tenant Isolation:** Multi-tenancy strictly enforced via `merchant_id` across databases, policies, and vector similarity retrieval.
- **Security Hardening:** Base32 TOTP MFA, SHA-256 password reset tokens, binary magic-byte inspection (JPEG, PNG, WEBP, PDF), and 10MB upload ceiling.
