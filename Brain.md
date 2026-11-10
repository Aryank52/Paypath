# PayPath — Project Brain

## 1. Project Identity
- **Name:** PayPath
- **Category:** AI Transaction Intelligence + Agentic Commerce + Payment Action Platform
- **Tagline:** *Understand. Decide. Act. Verify.*
- **Core Statement:** *PayPath turns PayPal transactions into intelligent, explainable, policy-controlled financial workflows.*

---

## 2. Product Vision & Architecture Paradigm
PayPath is an AI-powered intelligence layer around PayPal transactions covering the complete lifecycle:
```text
USER INTENT ➔ PURCHASE / PAYMENT PROPOSAL ➔ PAYMENT AUTHORIZATION ➔ PAYPAL TRANSACTION ➔
TRANSACTION INTELLIGENCE ➔ MONITORING ➔ ISSUE / RISK / EXCEPTION ➔ POLICY + RAG + EVIDENCE ➔
AI REASONING ➔ DETERMINISTIC POLICY ENGINE ➔ HUMAN APPROVAL ➔ PAYPAL ACTION ➔
INDEPENDENT VERIFICATION ➔ AUDIT TRAIL ➔ RESOLUTION
```

### The Non-Negotiable Core Principle
> **AI understands the transaction, policy systems constrain the decision, humans control consequential financial actions, PayPal performs the financial operation, and PayPath independently verifies the outcome.**

- **AI MAY:** Classify intent, search & recommend products, analyze evidence & receipts, interpret policy text, generate explanations & risk signals, propose candidate actions.
- **AI MUST NOT:** Fabricate transaction IDs, invent balances or refund amounts, bypass policies or approvals, receive unrestricted payment credentials, execute uncontrolled mutations, or declare success without verification.

---

## 3. Technology Stack Summary
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), PostgreSQL 16 (`127.0.0.1:5432/paypath`), Alembic.
- **Machine Learning Subsystem:** Scikit-Learn 1.9.1, XGBoost 3.4.1, Pandas 3.1.1. Deterministic 12-feature pipeline (`f12_v1`), Supervised XGBoost risk classifier, Unsupervised Isolation Forest anomaly detector, temporal 70/15/15 train/val/test split, explainability with top feature impact drivers, PostgreSQL registry (`ml_model_versions`, `ml_predictions`).
- **Core Payment Engine:** `app/paycore/` (PayPal REST API SDK/Client, OAuth2, Order creation, capture, refund, independent read-back verification, idempotency store, webhook processing).
- **AI & RAG Engine:** Multi-provider LLM abstraction, tenant-isolated vector store (`merchant_id` partitioning), cosine similarity matching, deterministic JSON schemas.
- **Agent Orchestrator:** Typed Agent-to-Agent message bus (Intent, Transaction, Shopping, Guard, Evidence, Resolution, Verification Agents).
- **Frontend:** React 19 / TypeScript, Vite 8.3, Tailwind CSS v4, AG Grid Enterprise/Community (Transaction Intelligence Explorer), Lucide Icons, Zustand store.
- **Observability & Diagnostics:** Live multi-subsystem health aggregation (`/api/v1/system/health`), full database row-count inventory (`/api/v1/system/database`), System Architecture UI (`SystemIntelligenceView.tsx`).

---

## 4. Current Implementation Status
- **Current Phase:** Phase 17 — Real Provider Activation, Live LLM/RAG Verification & PayPal Sandbox Certification.
- **Authoritative Database:** PostgreSQL 16.15 running on `127.0.0.1:5432/paypath`. All 20 tables active and verified (238 baseline seed records, 304 total live records persisted in PostgreSQL 16, including 7 agent runs and 30 tool calls).
- **External Providers:** Truth-based multi-state telemetry verified (`NOT_CONFIGURED`, `MOCK`, `CONFIGURED`, `CONNECTED`, `ERROR`). PayPal: `NOT_CONFIGURED` (ready for sandbox credentials in `.env`), LLM: `MOCK` (`deterministic-mock-v1` verified for structured intent extraction, ready for Gemini API key in `.env`). Simulated LLM failure verified to halt execution safely without financial side-effects.
- **Backend Test Suite:** 39/39 passing tests (100% green pass rate across unit, adversarial, security, ML pipeline, system health, and end-to-end integration).
- **Frontend State:** React 19.3.1 + Vite 8.3.6. Production build verified (`npm run build` completed cleanly in 5.03s with 0 errors). Live Provider Status Matrix and ML Benchmark validation disclosures integrated into `SystemIntelligenceView.tsx`.
- **Documentation:** Fully reconciled across `docs/FINAL_STATE_RECONCILIATION.md`, `docs/PROVIDER_STATUS.md`, `docs/RELEASE.md`, `docs/AGENT_SPEC.md`, `docs/DATA_ARCHITECTURE.md`, `docs/PRE_RELEASE_AUDIT.md`, `docs/GAP_ANALYSIS.md`.
- **System Certification Status:** `INTEGRATED WITH REMAINING PROVIDER CONFIGURATION`.

---

## 5. Major Architectural Decisions (ADRs)
1. **Separation of PayCore & AI:** All PayPal API calls are strictly encapsulated in `app/paycore/`. Agents cannot communicate with PayPal directly; they emit typed `ActionRequest` proposals that must pass the deterministic `PolicyEngine` and `ApprovalGateway`.
2. **Dual-Phase Resolution Verification:** After issuing a refund or capture via PayPal, PayPath does not trust the mutation response alone. A secondary read-back query (`GET /v2/payments/captures/{id}` or `GET /v2/payments/refunds/{id}`) is executed to independently verify state, currency, and amount.
3. **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries are converted into deterministic parameters. The deterministic engine evaluates these boundaries; ML/AI outputs are strictly non-authoritative advisory signals.
4. **PostgreSQL 16 Authoritative System of Record:** In-memory mocks and SQLite fallbacks were eliminated from the production runtime. All 20 entity tables are unified in PostgreSQL 16.
5. **Deterministic 12-Feature Leakage-Free ML Pipeline:** ML features strictly exclude post-settlement and dispute outcome fields. Temporal splitting respects sequence order (70% train, 15% val, 15% test).
