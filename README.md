# PayPath
## AI-Powered Transaction Intelligence, Agentic Commerce & Payment Action Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![AG Grid](https://img.shields.io/badge/AG_Grid-Data_Explorer-535353.svg?logo=ag-grid&logoColor=white)](https://www.ag-grid.com)
[![PayPal](https://img.shields.io/badge/PayPal-Sandbox_v2-00457C.svg?logo=paypal&logoColor=white)](https://developer.paypal.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Understand. Decide. Act. Verify.**  
> *PayPath turns PayPal transactions into intelligent, explainable, policy-controlled financial workflows.*

---

## 1. Executive Summary & Vision

Modern AI agents can search the web and converse about products, but granting autonomous AI direct access to financial transactions poses grave risks of hallucinated amounts, runaway spending, and policy violations.

**PayPath** solves the trust and control problem in agentic commerce through a foundational principle:

> **AI understands the transaction, policy systems constrain the decision, humans control consequential financial actions, PayPal performs the financial operation, and PayPath independently verifies the outcome.**

PayPath covers the complete transaction lifecycle:
```text
USER INTENT ➔ PURCHASE / PAYMENT PROPOSAL ➔ PAYMENT AUTHORIZATION ➔ PAYPAL TRANSACTION ➔
TRANSACTION INTELLIGENCE ➔ MONITORING ➔ ISSUE / RISK / EXCEPTION ➔ POLICY + RAG + EVIDENCE ➔
AI REASONING ➔ DETERMINISTIC POLICY ENGINE ➔ HUMAN APPROVAL ➔ PAYPAL ACTION ➔
INDEPENDENT VERIFICATION ➔ AUDIT TRAIL ➔ RESOLUTION
```

---

## 2. The Five Intelligence Modes

| Mode | Name | Key Question | Core Capabilities |
|---|---|---|---|
| **Mode 1** | **UNDERSTAND** | *What happened?* | PayPal transaction retrieval, lifecycle normalization, event timeline, AI health summaries, and AG Grid intelligence exploration. |
| **Mode 2** | **INTENT** | *What does the user want?* | Natural language intent extraction to structured constraints (budget, category, purpose, autonomy level). |
| **Mode 3** | **GUARD** | *Should this payment move?* | Pre-transaction authorization checks against spend limits, merchant trust scores, and human-in-the-loop gates (`ALLOW`, `REVIEW`, `BLOCK`, `ESCALATE`). |
| **Mode 4** | **RECOVER** | *What can be saved?* | Deterministic duplicate payment anomaly detection, recurring subscription tracking, and renewal alerting. |
| **Mode 5** | **RESOLVE (RECLAIM)** | *How is an issue resolved?* | End-to-end post-purchase dispute subsystem: photo damage inspection, merchant policy RAG retrieval, resolution recommendation, human approval, and PayPal refund verification. |

---

## 3. System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REACT FRONTEND (Vite)                           │
│  - AG Grid Explorer    - RECLAIM Center       - Payment Guard Studio        │
│  - AI Command Center   - Shopping Hub         - Audit & Agent Trace Stream  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND CORE                              │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │  Auth & RBAC Guards   │  │  Rate Limiting Engine │  │ Audit & Logging │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    API Route Controllers                              │  │
│  │  /auth  /transactions  /intent  /shop  /policies  /reclaim  /approvals │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────┴───────────────────────────────────┐  │
│  │            PAYPATH TRANSACTION INTELLIGENCE & AGENT ENGINE            │  │
│  │  ┌────────────────────────┐             ┌──────────────────────────┐  │  │
│  │  │   Agent Orchestrator   │◄───────────►│  Typed Agent Message Bus │  │  │
│  │  │ (Intent, Shopping,     │             │ (Validated Pydantic MSGs)│  │  │
│  │  │  Policy, Evidence,     │             └──────────────────────────┘  │  │
│  │  │  Risk, Resolution,     │                                           │  │
│  │  │  Verification, etc.)   │                                           │  │
│  │  └───────────┬────────────┘                                           │  │
│  │              │                                                        │  │
│  │              ▼                                                        │  │
│  │  ┌────────────────────────┐             ┌──────────────────────────┐  │  │
│  │  │    RAG Engine / Vector │             │ Deterministic Policy     │  │  │
│  │  │    pgvector / metadata │             │ Engine (ALLOW/REVIEW/    │  │  │
│  │  │    filtering & citation│             │ BLOCK/ESCALATE)          │  │  │
│  │  └────────────────────────┘             └────────────┬─────────────┘  │  │
│  └──────────────────────────────────────────────────────┼────────────────┘  │
│                                                         │                   │
│                                                         ▼                   │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         APPROVAL GATEWAY                              │  │
│  │  Human-in-the-loop: AUTO_ALLOWED | USER_APPROVAL | DUAL_APPROVAL     │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │ (Approved Mutations Only)            │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         PAYCORE SUBSYSTEM                             │  │
│  │  - PayPal REST OAuth2 Client   - Idempotency Vault                    │  │
│  │  - Order Creation & Capture    - Webhook Signature Verifier           │  │
│  │  - Refund Mutation Engine      - Independent Read-Back Verifier       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        ┌───────────────────────┐             ┌───────────────────────┐
        │     POSTGRESQL 16     │             │   PAYPAL SANDBOX API  │
        │ - Relational Tables   │             │ - Orders v2           │
        │ - pgvector Embeddings │             │ - Payments v2         │
        │ - Immutable Audit Log │             │ - Webhooks v1         │
        └───────────────────────┘             └───────────────────────┘
```

---

## 4. Multi-Agent Ecosystem
Instead of a single brittle prompt, PayPath organizes 8 specialized agents communicating via a typed message bus:
1. **Intent Agent:** Extracts entities, budgets, and autonomy flags from free-form natural language.
2. **Transaction Agent:** Ingests raw PayPal records, normalizes currency/timestamps, links customer history.
3. **Shopping Agent:** Queries product catalog (Channel3/normalized provider), applies constraints, proposes purchases.
4. **Policy Agent:** Searches indexed merchant & user policies via RAG, extracts relevant clauses with citations.
5. **Evidence Agent:** Inspects uploaded media (photos, receipts, invoices), detects damage or discrepancies.
6. **Risk Agent:** Computes anomaly scores, detects potential duplicate payments and abnormal merchant velocity.
7. **Resolution Agent:** Combines transaction data, policy citations, and evidence to formulate an actionable resolution proposal (e.g. `PARTIAL_REFUND`, `REPLACEMENT`).
8. **Verification Agent:** Queries PayPal directly post-mutation to independently confirm amount, currency, and final state.

---

## 5. PayCore & Independent PayPal Verification
PayPath enforces **dual-phase verification** on all financial mutations:
```text
Mutation Executed (Capture or Refund)
       ↓
Receive PayPal API Response
       ↓
Persist Pending Mutation Record
       ↓
Trigger Independent Read-Back (GET /v2/payments/captures/{id} or /refunds/{id})
       ↓
Verify: Status == COMPLETED, Currency == USD, Amount Matches Exactly
       ↓
Status Updated to "Verified by PayPal" (Rendered in UI)
```

---

## 6. Sponsor Integrations

1. **PayPal (Primary Hackathon Rail):** Complete sandbox integration in `backend/app/paycore/` covering Orders v2, Payments v2, Idempotency Vault, and Independent Verification.
2. **AG Grid (Data Grid Sponsor):** Powers the **Transaction Intelligence Explorer** with custom status renderers, risk badges, quick filtering, and lifecycle drawers.
3. **Render (Cloud Sponsor):** Full-stack infrastructure-as-code blueprint provided in `render.yaml` for FastAPI API, React Static Web, Managed PostgreSQL 16, and Redis.
4. **Postman (API Testing Sponsor):** End-to-end API test and workflow collection in `docs/postman/paypath.postman_collection.json`.
5. **Channel3 / Catalog:** Normalized product search adapter for the Shopping Agent.
6. **Elastic:** Structured audit event stream logging adapter.

---

## 7. Quick Start & Local Setup

### Prerequisites
- Python 3.12+
- Node.js v20+ and npm
- PostgreSQL 16 (optional; defaults seamlessly to async SQLite `sqlite+aiosqlite:///./paypath.db` for zero-setup local execution)

### 1. Backend Setup
```bash
# From repository root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend service
python backend/run.py
```
Backend will start on `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/api/v1/docs`.

### 2. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Run Test Suite
```bash
pytest
```

---

## 8. Hackathon Hero Demo Walkthrough

1. **User Intent:** Type: *"Find travel wireless noise-cancelling headphones under $100."*
2. **Agentic Commerce:** Intent Agent extracts constraints; Shopping Agent returns the **NovaSound ANC Pro ($89.00)**.
3. **Payment Guard:** Evaluates $89.00 against the $100.00 limit (`ALLOW - Requires Human Approval`).
4. **PayPal Purchase:** Click "Authorize Payment" -> PayCore creates and captures the order in PayPal Sandbox.
5. **AG Grid Explorer:** Transaction lands in the grid with an AI-generated health insight.
6. **Dispute & RECLAIM:** 14 days later, package arrives damaged. Click "Open RECLAIM Claim" and upload damage photo.
7. **RAG & Policy Evidence:** Evidence Agent identifies structural damage (94% confidence); Policy Agent retrieves Nova Electronics' 30-day transit defect policy.
8. **Resolution Proposal:** Resolution Agent proposes **$65.00 Partial Refund**; Policy Engine deterministically validates the rule.
9. **Human Approval & PayPal Settlement:** Click **"Approve $65.00 Refund"** -> PayCore executes PayPal Sandbox refund -> Verification Agent reads back PayPal resource -> Badge displayed: **"Verified by PayPal"**.

---

## 9. Security & Governance

- **Zero Secret Exposure:** PayPal client secrets and API keys reside exclusively in server-side environment variables.
- **Idempotency Protection:** All mutation endpoints enforce `X-Idempotency-Key` to eliminate double charges or duplicate refunds.
- **Strict Multi-Tenancy:** Multi-tenant boundaries (`merchant_id`, `user_id`) enforced at the database query layer.
- **Defense-in-Depth AI:** User documents and policy text are isolated to prevent prompt injection.

---

## 10. License
This project is licensed under the [MIT License](LICENSE).
