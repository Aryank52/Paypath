# PayPath — Project Memory

## 1. Environment & Infrastructure Knowledge
- **Host OS:** Windows 11 (64-bit).
- **Runtimes:**
  - Python 3.12.10 (virtual environment active at `.venv/`)
  - Node.js v24.16.0 & npm 11.13.0
  - PostgreSQL 16.15 service running authoritative on `127.0.0.1:5432`, database `paypath`.
  - Silent SQLite fallback completely removed; PostgreSQL 16 is authoritative in development & production.
  - Git repository on `main` branch.

## 2. Tested & Verified Capabilities
- **Backend Test Suite:** 23 tests passing in `backend/tests/` (100% pass rate):
  - `test_policy_engine.py`: Evaluates spend caps, user intent budgets, blocked categories, return windows, damage coverage, and refund limits.
  - `test_agents.py`: Verified IntentAgent, ShoppingAgent, PolicyAgent, RiskAgent, EvidenceAgent, and ResolutionAgent.
  - `test_paycore_reclaim.py`: End-to-end integration test verifying PayPal Sandbox order creation, capture, independent read-back verification, RAG policy retrieval, human approval, refund mutation, and state transition to `VERIFIED`.
  - `test_api_endpoints.py`: Verified health check, transactions feed, intent parser, dispute cases, and notification lifecycle.
  - `test_mfa_and_upload_security.py`: Verified TOTP generation and clock skew tolerance, password reset token hashing & 1-hour expiration, and binary magic-byte inspection.
  - `test_security_and_edge_cases.py`: Verified prompt injection defense, idempotency replay prevention, and webhook deduplication.
- **Frontend Production Build:** Vite build succeeded with 0 errors in 2.96s (`dist/assets/index-*.js`, `dist/assets/index-*.css`).
- **Live Localhost Connectivity Verified:**
  - FastAPI ASGI Uvicorn server: Running on `http://127.0.0.1:8000` (PID 29172). Health endpoint reports `{"status": "HEALTHY", "database": "PostgreSQL 16", "database_status": "CONNECTED"}`.
  - Vite Dev server: Running on `http://127.0.0.1:5173` (PID active).
  - Reverse Proxy: Tested and verified `http://127.0.0.1:5173/api/v1/transactions` successfully returns seeded PostgreSQL transactions.
- **Data Grid Integration:** AG Grid Community integrated with custom renderers, quick filter, and row hover prefetching.
- **Documentation Suite:** 30 complete technical specifications and guides residing in `docs/`.

## 3. Key Design Conventions
- **Dual-Phase Read-Back Verification:** Mutating actions (`capture_order`, `execute_refund`) query PayPal directly post-mutation to compare actual vs. expected amount, currency, and completion status.
- **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries feed into the deterministic `PolicyEngine`. AI models do not possess final authorization authority.
- **Idempotency Protection:** Every financial mutation enforces unique idempotency keys (`payment_actions.idempotency_key`), preventing duplicate transactions or duplicate refunds.
- **Tenant Isolation:** Multi-tenancy strictly enforced via `merchant_id` across databases, policies, and vector similarity retrieval.
- **Security Hardening:** Base32 TOTP MFA, SHA-256 password reset tokens, binary magic-byte inspection (JPEG, PNG, WEBP, PDF), and 10MB upload ceiling.
