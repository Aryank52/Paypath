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
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, PostgreSQL + pgvector, Redis (fallback memory/rate limiter).
- **Core Payment Engine:** `app/paycore/` (PayPal REST API SDK/Client, OAuth2, Order creation, capture, refund, independent read-back verification, webhook signature verification, idempotency store).
- **AI & RAG Engine:** Multi-provider LLM abstraction (Gemini / OpenAI / Anthropic / local mock fallback), pgvector semantic embeddings, deterministic structured JSON schemas.
- **Agent Orchestrator:** Typed Agent-to-Agent message bus (Intent, Transaction, Shopping, Policy, Evidence, Risk, Resolution, Verification, Notification, Merchant Agents).
- **Frontend:** React 19 / TypeScript, Vite, Tailwind CSS v4, AG Grid Enterprise/Community (Transaction Intelligence Explorer), TanStack Query v5, Lucide Icons, Zustand.
- **Sponsor Integrations:** PayPal (Core), AG Grid (Data Grid & Intelligence Explorer), Render (Hosting/Background Workflows), Postman (API Suite), Channel3 (Product Catalog / Commerce), Elastic (Audit Observability & Hybrid Search), Bryntum (Timeline/Gantt Resolution), APIMatic (API Contracts).

---

## 4. Current Implementation Status
- **Current Phase:** Phase 0 & Phase 1 — Project Initialization, Architecture Specifications, Foundation Setup.
- **Repository State:** Clean workspace initialized on Windows (Python 3.12, Node 24, npm 11).
- **Blockers:** None.
- **Active Focus:** Establishing project memory, comprehensive documentation, base database models, PayCore PayPal engine, and interactive frontend.

---

## 5. Major Architectural Decisions (ADRs)
1. **Separation of PayCore & AI:** All PayPal API calls are strictly encapsulated in `app/paycore/`. Agents cannot communicate with PayPal directly; they emit typed `ActionRequest` proposals that must pass the deterministic `PolicyEngine` and `ApprovalGateway`.
2. **Dual-Phase Resolution Verification:** After issuing a refund or capture via PayPal, PayPath does not trust the mutation response alone. A secondary read-back query (`GET /v2/payments/captures/{id}` or `GET /v2/payments/refunds/{id}`) is executed to independently verify state, currency, and amount.
3. **Deterministic Policy Precedence:** RAG-retrieved policies and LLM summaries are converted into deterministic parameters (e.g. `refund_window_days`, `max_auto_refund_amount`). The deterministic engine evaluates these boundaries; the LLM never has the final authorization authority.
4. **Resilient Fallback Providers:** Every external service (PayPal Sandbox, LLM, Product Catalog, Redis, Elastic) implements an interface with an offline/demo fallback mode so the platform operates reliably in any demo environment.

---

## 6. Demo Golden Path
1. **User Intent:** Natural language shopping request (*"Find travel noise-cancelling headphones under $100"*).
2. **Agentic Commerce:** Shopping Agent parses intent, queries catalog, validates price guardrail.
3. **Payment Authorization (Guard):** Intent checked against budget limit ($100), policy evaluated, user approves.
4. **PayPal Execution:** PayCore creates PayPal order, user completes sandbox checkout, payment captured.
5. **Transaction Intelligence:** Transaction lands in AG Grid with AI lifecycle summary, metadata, and event timeline.
6. **Exception & Resolution (RECLAIM):** User reports damaged delivery, uploads photo evidence.
7. **RAG & Evidence Analysis:** Evidence Agent identifies physical damage; Policy Agent retrieves merchant refund policy.
8. **Policy & Approval:** Resolution Agent proposes $65 partial refund; Policy Engine verifies eligibility; Human approves.
9. **PayPal Action & Independent Verification:** PayCore executes refund on PayPal sandbox; Verification Agent re-reads PayPal API to confirm refunded status; status marked **Verified by PayPal**.
10. **Audit Trail:** Immutable timeline updated with cryptographic hashes and step-by-step agent traces.

