# PayPath — System Architecture

## 1. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REACT FRONTEND (Vite)                           │
│  - AG Grid Explorer    - RECLAIM Center       - Payment Guard Studio        │
│  - AI Command Center   - Shopping Hub         - Audit & Agent Trace Stream  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / WSS / JSON
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

## 2. Agent Ecosystem & Message Bus
The agent framework uses decoupled, specialized agents communicating over a validated schema:
1. **Intent Agent:** Extracts entities, constraints, budgets, and autonomy flags from free-form natural language.
2. **Transaction Agent:** Ingests raw PayPal payloads, normalizes currency/timestamps, links customer history.
3. **Shopping Agent:** Queries product catalog (Channel3/normalized provider), applies constraints, proposes purchases.
4. **Policy Agent:** Searches indexed merchant & user policies via RAG, extracts relevant clauses with citations.
5. **Evidence Agent:** Inspects uploaded media (photos, receipts, invoices), detects damage or discrepancies.
6. **Risk Agent:** Computes anomaly scores, detects potential duplicate payments and abnormal merchant velocity.
7. **Resolution Agent:** Combines transaction data, policy citations, and evidence to formulate an actionable resolution proposal (e.g. `PARTIAL_REFUND`, `REPLACEMENT`).
8. **Verification Agent:** Queries PayPal directly post-mutation to independently confirm amount, currency, and final state.
9. **Notification Agent:** Dispatches in-app and webhook alerts based on workflow progression.
10. **Merchant Agent:** Manages merchant policy ingestion, chunking, and tenant-level configurations.

---

## 3. Financial Action State Machine
Any financial mutation (Capture, Refund, Authorization) transitions through explicit immutable states:
```text
PROPOSED ➔ VALIDATING ➔ AWAITING_APPROVAL ➔ APPROVED ➔ EXECUTING ➔ EXECUTED ➔ VERIFYING ➔ VERIFIED
    │          │               │               │           │                     │
    ▼          ▼               ▼               ▼           ▼                     ▼
 REJECTED   BLOCKED         REJECTED        REJECTED     FAILED               MISMATCH
```

---

## 4. Database Schema Structure
- **Core Entities:** `users`, `merchants`, `merchant_policies`, `policy_versions`, `policy_chunks`.
- **Commerce & Intent:** `purchase_intents`, `shopping_sessions`, `products`, `orders`.
- **Payments & Audit:** `transactions`, `transaction_events`, `payment_actions`, `payment_verifications`, `audit_logs`.
- **Intelligence & Exceptions:** `risk_signals`, `duplicate_signals`, `subscriptions`, `evidence`, `evidence_analysis`.
- **Resolutions & Approvals:** `decisions`, `approvals`, `resolutions`, `notifications`, `agent_runs`, `agent_messages`.

---

## 5. Security & Isolation Controls
- **Data Isolation:** All queries filter by `tenant_id` / `merchant_id` and authenticated `user_id`.
- **Credential Safety:** PayPal secrets, API keys, and JWT secrets reside exclusively in server-side environment variables.
- **Idempotency Protection:** Every financial mutation uses an `Idempotency-Key` persisted in the database; duplicate submissions return cached results without re-executing.
- **Input Sanitization:** Multi-layered defense against SQL injection, XSS, and LLM prompt injection (prompt framing & strict schema parsing).
