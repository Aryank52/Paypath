# PayPath — System Architecture

## 1. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REACT FRONTEND (Vite)                           │
│  - AG Grid Explorer    - RECLAIM Center       - Payment Guard Studio        │
│  - AI Command Center   - Shopping Hub         - System Architecture View    │
│  - ML Simulator        - Audit & Agent Trace  - Merchant Intelligence       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND CORE                              │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │  Auth & RBAC Guards   │  │  Rate Limiting Engine │  │ Audit & Logging │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    API Route Controllers                              │  │
│  │  /auth /transactions /paycore /intent /shop /guard /reclaim /policies │  │
│  │  /ml /system /merchants /webhooks /notifications /audit               │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────┴───────────────────────────────────┐  │
│  │            PAYPATH TRANSACTION INTELLIGENCE & AGENT ENGINE            │  │
│  │  ┌────────────────────────┐             ┌──────────────────────────┐  │  │
│  │  │   Agent Orchestrator   │◄───────────►│  Typed Agent Message Bus │  │  │
│  │  │ (Intent, Shopping,     │             │ (Validated Pydantic MSGs)│  │  │
│  │  │  Guard, Evidence,      │             └──────────────────────────┘  │  │
│  │  │  Resolution, Verifier) │                                           │  │
│  │  └───────────┬────────────┘                                           │  │
│  │              │                                                        │  │
│  │              ▼                                                        │  │
│  │  ┌────────────────────────┐             ┌──────────────────────────┐  │  │
│  │  │   RAG Engine / Vector  │             │   ML Subsystem (12-Feat  │  │  │
│  │  │  Tenant-isolated chunks│             │   XGBoost + Isol Forest) │  │  │
│  │  │  & merchant policies   │             │   Non-authoritative      │  │  │
│  │  └───────────┬────────────┘             └────────────┬─────────────┘  │  │
│  │              │                                       │                │  │
│  │              ▼                                       ▼                │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │       Deterministic Policy Engine (ALLOW/REVIEW/MFA/BLOCK)    │  │  │
│  │  └───────────────────────────────┬───────────────────────────────┘  │  │
│  └──────────────────────────────────┼──────────────────────────────────┘  │
│                                     │                                       │
│                                     ▼                                       │
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
        │ - 20 Relational Tables│             │ - Orders v2           │
        │ - pgvector & ML Models│             │ - Payments v2         │
        │ - Immutable Audit Log │             │ - Webhooks v1         │
        └───────────────────────┘             └───────────────────────┘
```

---

## 2. Agent Ecosystem & Message Bus
The agent framework uses decoupled, specialized agents communicating over a validated schema:
1. **Intent Agent:** Extracts entities, constraints, budgets, and autonomy flags from free-form natural language.
2. **Shopping Agent:** Queries product catalog, applies constraints, recommends products.
3. **Guard Agent:** Pre-transaction compliance gatekeeper checking user velocity, category restrictions, and ML anomaly scores.
4. **Policy Agent:** Searches indexed merchant & user policies via RAG with tenant isolation.
5. **Evidence Agent:** Inspects uploaded media with magic-byte validation and multi-modal damage diagnosis.
6. **Resolution Agent:** Combines transaction data, policy citations, and evidence to formulate actionable settlement proposals.
7. **Verification Agent:** Queries PayPal directly post-mutation to independently confirm amount, currency, and final state.

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

## 4. Authoritative Database Schema (20 PostgreSQL 16 Tables)
- **Identity & Access:** `users`, `audit_logs`.
- **Merchant & Catalog:** `merchants`, `products`, `merchant_policies`, `policy_chunks`.
- **Transactions & PayCore:** `transactions`, `transaction_events`, `purchase_intents`, `payment_actions`, `payment_verifications`, `subscriptions`.
- **RECLAIM & Evidence:** `reclaim_cases`, `evidence`.
- **Machine Learning & Registry:** `ml_model_versions`, `ml_predictions`.
- **Multi-Agent Orchestration:** `agent_runs`, `agent_tool_calls`.
- **Notifications & Telemetry:** `notifications`.

---

## 5. Security & Isolation Controls
- **PostgreSQL 16 Authoritative:** Zero SQLite or in-memory fallback in production runtime.
- **Data Isolation:** All queries filter by `merchant_id` and authenticated `user_id`.
- **Idempotency Protection:** Every financial mutation uses an `idempotency_key` stored in `payment_actions`.
- **Dual-Phase Verification:** Mutation status confirmed via direct API read-back from PayPal before declaring completion.
- **Advisory ML Safety:** Machine learning models are non-authoritative. Output scores provide signals to deterministic policy systems.
