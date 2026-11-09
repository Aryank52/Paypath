# PayPath — Project Memory

## 1. Environment & Infrastructure Knowledge
- **Host OS:** Windows 11 (64-bit).
- **Runtimes:**
  - Python 3.12.10 (virtual environment active at `.venv/`)
  - Node.js v24.16.0 & npm 11.13.0
  - PostgreSQL 16 service available; zero-setup local dev runs on async SQLite (`sqlite+aiosqlite:///./paypath.db`) with identical SQLAlchemy async dialect abstraction.
  - Git repository on `main` branch.

## 2. Tested & Verified Capabilities
- **Backend Test Suite:** 16 tests passing in `backend/tests/` (100% pass rate):
  - `test_policy_engine.py`: Evaluates spend caps, user intent budgets, blocked categories, return windows, damage coverage, and refund limits.
  - `test_agents.py`: Verified IntentAgent, ShoppingAgent, EvidenceAgent, and ResolutionAgent.
  - `test_paycore_reclaim.py`: End-to-end integration test verifying PayPal Sandbox order creation, capture, independent read-back verification, RAG policy retrieval, human approval, refund mutation, and state transition to `VERIFIED`.
  - `test_api_endpoints.py`: Verified health check, transactions feed, intent parser, payment guard, and multi-agent commerce workflows.
- **Frontend Production Build:** Vite build succeeded with 0 errors in 2.92s (`dist/assets/index-*.js`, `dist/assets/index-*.css`).
- **Data Grid Integration:** AG Grid Community successfully integrated with custom renderers for status pills, risk badges, and lifecycle drawers.
- **Postman API Suite:** Exported to `docs/postman/paypath.postman_collection.json`.
- **Render Deployment Blueprint:** Declarative `render.yaml` created for full-stack cloud deployment.

## 3. Key Design Conventions
- **Dual-Phase Read-Back Verification:** Mutating actions (`capture_order`, `execute_refund`) query PayPal directly post-mutation to compare actual vs. expected amount, currency, and completion status.
- **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries feed into the deterministic `PolicyEngine`. AI models do not possess final authorization authority.
- **Idempotency Protection:** Every financial mutation enforces unique idempotency keys (`payment_actions.idempotency_key`), preventing duplicate transactions or duplicate refunds.
- **Tenant Isolation:** Multi-tenancy strictly enforced via `merchant_id` across databases, policies, and vector similarity retrieval.
