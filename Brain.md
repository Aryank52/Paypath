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
- **Current Phase:** Master Phase 24 — Full Functional Audit, Security Re-Audit, PayPal Capability Audit & Final Product Completion.
- **Authoritative Database:** PostgreSQL 16.15 running on `127.0.0.1:5432/paypath`. All 21 public tables active and verified (`users`, `merchants`, `products`, `merchant_policies`, `policy_chunks`, `transactions`, `transaction_events`, `reclaim_cases`, `evidence`, `subscriptions`, `notifications`, `ml_model_versions`, `ml_predictions`, `agent_runs`, `agent_tool_calls`, `purchase_intents`, `payment_actions`, `payment_verifications`, `audit_logs`, `webhook_events`, `alembic_version`).
- **External Providers:** Truth-based multi-state telemetry verified. PostgreSQL: `CONNECTED`, PayPal Sandbox: `CONNECTED` (`api-m.sandbox.paypal.com` token verified), Gemini: `CONNECTED` (`gemini-2.5-flash` operational), RAG: `ACTIVE` (19 chunks), ML: `VALIDATED` (XGBoost v1.0.0, Isolation Forest v1.0.0).
- **Backend Test Suite:** 53/53 passing tests (100% green pass rate in 67s across all unit, adversarial, security, IDOR, RBAC, ML, PayPal webhook, and end-to-end integration suites).
- **Frontend State:** React 19 + TypeScript + Vite. Production build verified (`npm run build` completed cleanly in 4.09s with 0 errors). Premium Fintech Minimalism + Bento Grid design implemented. India DPDP Act 2023 compliance, Grievance Officer disclosures (`grievance@paypath.finance`), and RECLAIM refund disclosures fully active.
- **Audit Documentation Suite:** 7 authoritative documents created under `docs/`:
  1. `docs/API_TRACE_MATRIX.md` (30 end-to-end interactions traced)
  2. `docs/FEATURE_COMPLETENESS_AUDIT.md` (22/22 features operational)
  3. `docs/UI_UX_AUDIT.md` (Zero AI-slop, WCAG 2.2 contrast verified)
  4. `docs/PAYPAL_CAPABILITY_AUDIT.md` (12 capabilities evaluated, idempotency verified)
  5. `docs/RAG_EVALUATION.md` (7 scenarios tested, 100% ground truth citation accuracy)
  6. `docs/SECURITY_REAUDIT.md` (78 baseline controls + 4 Gate A controls passing)
  7. `docs/PRODUCTION_FUNCTIONAL_AUDIT.md` (8 user journeys verified)
- **System Certification Status:** `PRODUCTION FUNCTIONAL & SECURITY CERTIFIED (v1.0.0)`.

---

## 5. Major Architectural Decisions (ADRs)
1. **Separation of PayCore & AI:** All PayPal API calls are strictly encapsulated in `app/paycore/`. Agents cannot communicate with PayPal directly; they emit typed `ActionRequest` proposals that must pass the deterministic `PolicyEngine` and `ApprovalGateway`.
2. **Dual-Phase Resolution Verification:** After issuing a refund or capture via PayPal, PayPath does not trust the mutation response alone. A secondary read-back query (`GET /v2/payments/captures/{id}` or `GET /v2/payments/refunds/{id}`) is executed to independently verify state, currency, and amount.
3. **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries are converted into deterministic parameters. The deterministic engine evaluates these boundaries; ML/AI outputs are strictly non-authoritative advisory signals.
4. **PostgreSQL 16 Authoritative System of Record:** In-memory mocks and SQLite fallbacks were eliminated from the production runtime. All 20 entity tables are unified in PostgreSQL 16.
5. **Deterministic 12-Feature Leakage-Free ML Pipeline:** ML features strictly exclude post-settlement and dispute outcome fields. Temporal splitting respects sequence order (70% train, 15% val, 15% test).
