# PayPath
## AI Transaction Intelligence & Agentic Commerce

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.3.1-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![AG Grid](https://img.shields.io/badge/AG_Grid-36.3.0-535353.svg?logo=ag-grid&logoColor=white)](https://www.ag-grid.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.15-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![PayPal](https://img.shields.io/badge/PayPal-Sandbox_v2-00457C.svg?logo=paypal&logoColor=white)](https://developer.paypal.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Understand. Decide. Act. Verify.**  
> *PayPath turns financial transactions into explainable, policy-controlled, and independently verified workflows for the agentic economy.*

---

### 🌐 Live Production Deployments & Access

| Resource | Live Endpoint | Purpose |
|---|---|---|
| **Frontend Application** | [https://paypath-hazel.vercel.app/](https://paypath-hazel.vercel.app/) | Official React 19 production deployment on Vercel |
| **Backend API Core** | [https://paypath-8u9a.onrender.com](https://paypath-8u9a.onrender.com) | FastAPI production service on Render |
| **Health Check** | [https://paypath-8u9a.onrender.com/health](https://paypath-8u9a.onrender.com/health) | Live runtime diagnostic and subsystem readiness |
| **Interactive API Docs** | [https://paypath-8u9a.onrender.com/api/v1/docs](https://paypath-8u9a.onrender.com/api/v1/docs) | Interactive Swagger / OpenAPI documentation |
| **Repository** | [https://github.com/Aryank52/Paypath](https://github.com/Aryank52/Paypath) | Public source repository on GitHub |

### 🔑 Demo Access

Demo credentials are provided privately for judges/evaluators. Contact the project owner for access.

---

## 1. Executive Summary & The Problem

Autonomous AI agents are rapidly entering digital commerce: browsing catalogs, summarizing options, negotiating terms, and initiating purchases. However, **granting autonomous AI direct, unconstrained access to financial execution creates severe systemic risks**:
- **Hallucinated Amounts & Parameters:** Generative models can hallucinate discount codes, amounts, currencies, or order quantities.
- **Runaway Agent Spending:** Without deterministic constraints, agent loops can exhaust budgets or repeatedly trigger billing cycles.
- **Policy Violations & Compliance Failures:** Large Language Models are probabilistic and cannot guarantee deterministic adherence to corporate expense policies or statutory refund windows.
- **Lack of Non-Repudiation:** Traditional agent workflows lack tamper-evident audit trails linking intent to approval, mutation, and downstream payment verification.

**PayPath** bridges the trust gap between generative AI and payment rails. It provides a hardened financial operating system where AI provides advisory intelligence, but every monetary movement is governed by deterministic rules, authenticated human approvals, and independent payment rail verification.

---

## 2. Core Principle

PayPath operates under an uncompromising architectural axiom:

> **"AI interprets. RAG provides context. ML provides advisory intelligence. Deterministic policies control decisions. Humans approve consequential actions. PayPal executes. PayPath verifies."**

Under no circumstance is an LLM or ML model permitted to directly authorize or execute a financial movement. AI suggests; deterministic code enforces; authenticated humans decide; PayPal settles; PayPath independently verifies.

---

## 3. Key Capabilities

### 🔍 1. Transaction Intelligence Explorer (AG Grid)
- **High-Performance Enterprise Grid:** Powered by AG Grid Community 36.3.0 with custom cell renderers for status badges, risk chips, and PayPal state indicators.
- **Multi-Column Filtering & Sorting:** Instant client-side and server-side filtering across amounts, merchants, categories, and date ranges.
- **AI Health Insights:** Pre-computed explainable transaction breakdowns identifying billing anomalies, recurring charges, and dispute eligibility.
- **Lifecycle Detail Drawers:** Slide-over inspection drawers displaying immutable audit timelines and PayPal read-back confirmation.

### 🎯 2. AI / Intent Hub
- **Natural Language Intent Parsing:** Converts free-form shopper or enterprise prompts into structured financial proposals (target item, category, max price, autonomy level).
- **Constrained Extraction:** Employs strictly typed Pydantic models to guarantee valid numeric ranges and ISO-4217 currency codes.

### 🛡️ 3. Deterministic Payment Guard
- **Pre-Authorization Policy Engine:** Evaluates prospective purchases against deterministic spend limits, velocity rules, merchant trust scores, and category blacklists.
- **Strict State Machine:** Issues one of four immutable verdicts: `ALLOW`, `REVIEW`, `BLOCK`, or `ESCALATE`.
- **Zero Hallucination Risk:** Policy decisions execute in pure Python logic independent of LLM inferences.

### 🛍️ 4. Guarded Shopping
- **Agentic Commerce with Guardrails:** Enables autonomous product research and comparison while enforcing hard spending budgets.
- **Sanitized Proposals:** Verifies merchant identity, tax calculations, and shipping fees before constructing payment orders.

### 🔄 5. Recovery Intelligence
- **Deterministic Duplicate Detection:** Analyzes sliding time windows for identical merchant, currency, and amount collisions.
- **Subscription Waste Identification:** Uncovers recurring subscription creep, unannounced price increases, and forgotten recurring billing.

### ⚖️ 6. RECLAIM Dispute & Resolution Engine
- **End-to-End Post-Purchase Resolution:** Guides users through structured disputes for damaged goods, non-delivery, or incorrect billing.
- **Multi-Modal Evidence Inspection:** Validates uploaded receipts and damage photos with magic-byte security inspection.
- **Policy-Aware Proposals:** Compares dispute circumstances against merchant return policies to generate legally grounded refund proposals.

### 🏛️ 7. Merchant Policy Studio
- **Document Ingestion:** Ingests raw merchant terms, cancellation policies, and warranty rules.
- **Vectorized Policy Knowledge:** Indexes clauses into PostgreSQL using `pgvector` for accurate semantic matching during claim processing.

### 🔒 8. Tenant-Isolated RAG
- **Zero Cross-Tenant Leakage:** Every vector search query strictly enforces relational tenant scoping (`tenant_id = :tenant_id`).
- **Precise Citation Backing:** Every policy retrieval includes source section references and clause excerpts.

### 📊 9. Leakage-Free Machine Learning
- **Dual-Model Architecture:** Combines an XGBoost Classifier (transaction risk scoring) with an Isolation Forest (unsupervised anomaly detection).
- **12 Strict Behavioral Features:** Engineered strictly from non-leaking transaction attributes (amount, velocity, merchant tenure, hour-of-day, historical variance).
- **Strictly Advisory Role:** ML scores provide contextual risk signals (`0.0 - 1.0`) to human operators and deterministic policies; they never make unilateral settlement decisions.

### 🤖 10. Multi-Agent Workflows
- **Specialized Agent Roster:** Seven decoupled, domain-specific agents (Intent, Transaction, Shopping, Policy, Evidence, Risk, and Resolution).
- **Typed Message Bus:** Agents communicate strictly via validated Pydantic message envelopes with end-to-end correlation IDs.

### 💳 11. Full PayPal Integration
- **Orders v2 & Payments v2:** Production-ready implementation of PayPal OAuth2 client credentials, order creation, capture, and refunds.
- **Idempotency Vault:** Cryptographic request hashing prevents duplicate double-charges on network retries or concurrent clicks.

### 🔐 12. Webhook Signature Verification
- **Cryptographic Assurance:** Validates PayPal webhook signatures using RSA-SHA256, public cert retrieval, and payload CRC32 verification.
- **Replay Protection:** Rejects duplicate webhook deliveries through event ID caching.

### 🔁 13. Dual-Phase Read-Back Verification
- **Post-Mutation Read-Back:** After executing any mutation (order capture or refund), PayPath independently polls the PayPal API (`GET /v2/payments/captures/{id}` or `GET /v2/payments/refunds/{id}`).
- **Independent Reconciliation:** Confirms that status is `COMPLETED`, currency is `USD`, and the settled amount mathematically equals the requested amount before updating the authoritative database.

### 📜 14. Audit Trail & Governance
- **Append-Only Event Ledger:** Every user interaction, policy evaluation, agent message, and financial mutation is recorded in an immutable audit table.
- **Correlation Tracking:** End-to-end UUID correlation IDs follow every request from React frontend to PayPal settlement.

### 🛡️ 15. Security & Control Center
- **Granular RBAC:** Strict separation of privileges across `USER`, `MERCHANT_ADMIN`, and `PLATFORM_ADMIN` roles.
- **RFC 6238 TOTP MFA:** Two-factor authentication with time-based one-time password verification.
- **Session Revocation:** JWT `jti` blocklisting enables instantaneous session termination on logout.
- **Fail-Closed Architecture:** If an external service or storage bucket is unreachable or misconfigured, the platform fails closed rather than falling back to unverified defaults.

---

## 4. System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLIENT TIER: REACT 19 FRONTEND (Vercel)                │
│  - AG Grid Intelligence Explorer       - RECLAIM Dispute & Claims Studio   │
│  - Guarded Shopping Hub                - Payment Guard & Policy Rules       │
│  - Multi-Tenant RBAC UI (User / Merchant / Platform Admin)                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS (JSON / REST API)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 APPLICATION TIER: FASTAPI BACKEND CORE (Render)             │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │ JWT / JTI / TOTP Auth │  │  Role-Based Access    │  │ Rate Limiter    │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ API Routing: /auth, /transactions, /intent, /shop, /reclaim, /policies│  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────┴───────────────────────────────────┐  │
│  │                   INTELLIGENCE & AGENT ENGINE                         │  │
│  │  ┌─────────────────────────┐             ┌─────────────────────────┐  │  │
│  │  │   Agent Orchestrator    │◄───────────►│  Typed Pydantic Bus     │  │  │
│  │  │ (Intent, Shopping,      │             │ (End-to-End Correlation)│  │  │
│  │  │  Evidence, Resolution)  │             └─────────────────────────┘  │  │
│  │  └───────────┬─────────────┘                                          │  │
│  │              │                                                        │  │
│  │              ▼                                                        │  │
│  │  ┌─────────────────────────┐             ┌─────────────────────────┐  │  │
│  │  │ Advisory ML Engine      │             │ Tenant-Isolated RAG     │  │  │
│  │  │ (XGBoost + IsoForest)   │             │ (pgvector + Metadata)   │  │  │
│  │  └───────────┬─────────────┘             └────────────┬────────────┘  │  │
│  └──────────────┼────────────────────────────────────────┼───────────────┘  │
│                 │                                        │                  │
│                 ▼                                        ▼                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │               DETERMINISTIC PAYMENT GUARD & POLICY ENGINE             │  │
│  │         Rules: ALLOW | REVIEW | BLOCK | ESCALATE (Zero LLM Ambiguity) │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │ (Requires Human Approval)            │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    PAYCORE EXECUTION & VERIFICATION                   │  │
│  │  - PayPal REST OAuth2 Client        - Idempotency Request Vault       │  │
│  │  - Orders & Refunds v2 Executor     - Dual-Phase Read-Back Verifier   │  │
│  │  - RSA-SHA256 Webhook Validator     - Magic-Byte Evidence Inspector   │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│     POSTGRESQL 16     │  │   PAYPAL SANDBOX API  │  │   SUPABASE STORAGE    │
│  (Render Managed DB)  │  │   (Payments Rail)     │  │   (Evidence Files)    │
│ - Authoritative DB    │  │ - Orders v2           │  │ - Private Bucket Only │
│ - 20 Relational Tables│  │ - Payments v2 Capture │  │ - Fail-Closed Design  │
│ - 399 Verified Records│  │ - Refunds & Webhooks  │  │ - Server-Side Auth    │
│ - pgvector Embeddings │  │ - Idempotency Vault   │  │ - Zero DB Connection  │
│ - Immutable Audit Log │  │ - Read-Back Verifier  │  │   (Files Only)        │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
```

### Authoritative Database & Storage Separation
- **Render Managed PostgreSQL 16.15:** The **sole authoritative application database** for all relational entities, transactions, users, merchant policies, embeddings, and audit logs.
- **Supabase Storage:** Used **strictly for evidence file storage** (damage photos, receipts). No transactional data or application tables reside in Supabase.
- **Supabase PostgreSQL:** **NOT** the application database. PayPath maintains zero connection pools to Supabase PostgreSQL.

---

## 5. Technology Stack

| Layer | Technology | Verified Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | React | 19.3.1 | High-performance user interface |
| **Frontend Tooling** | Vite | 8.3.7 | Fast build and development server |
| **Language (UI)** | TypeScript | 7.0.2 | Type-safe client components |
| **UI Styling** | Tailwind CSS | 4.3.5 | Clean modern utility design system |
| **UI Icons** | Lucide React | 1.70.0 | Icon library |
| **Data Grid** | AG Grid Community / React | 36.3.0 | Enterprise transaction intelligence explorer |
| **State Management** | Zustand | 5.1.0 | Reactive lightweight client store |
| **Server State** | TanStack React Query | 5.107.1 | Asynchronous server-state management |
| **Backend Framework** | FastAPI | 0.115.8 | Async REST API application server |
| **Language (API)** | Python | 3.12.10 | High-throughput backend execution |
| **Validation** | Pydantic v2 | 2.10.6 | Strict data modeling and message validation |
| **ORM / Data Access** | SQLAlchemy 2 (asyncio) | 2.0.38 | Asynchronous database abstraction |
| **Database Driver** | asyncpg | 0.30.0 | High-performance async PostgreSQL driver |
| **Database Migrations**| Alembic | 1.14.1 | Schema versioning (migration head `82098dca4be4`) |
| **Application Database**| PostgreSQL (Render Managed) | 16.15 | 20 canonical tables, 399 authoritative records |
| **Vector Search** | pgvector | 0.3+ | Tenant-isolated policy embeddings |
| **Machine Learning** | XGBoost / Scikit-learn | 3.4.1 / 1.9.1 | Advisory transaction risk & anomaly detection |
| **File Storage** | Supabase Storage | v2 | Private bucket (`paypath-evidence`) for RECLAIM files |
| **Payment Rails** | PayPal REST APIs | v2 | Orders v2, Payments v2, Webhooks v1 (Sandbox) |
| **Hosting & Cloud** | Vercel (UI) / Render (API + DB)| Cloud | Edge frontend CDN and managed backend services |
| **Testing** | pytest, pytest-asyncio | 8.3.4 / 0.25.3 | Automated unit, integration, and security tests |

---

## 6. Security & Trust Model

PayPath enforces a defense-in-depth security architecture designed for financial operations:

1. **Deterministic Decision Authority:** LLMs and ML models are strictly advisory. No AI output can execute transactions or alter balances without passing deterministic policy evaluation.
2. **Strict Multi-Tenancy (No Cross-Tenant Leakage):** All database queries, vector similarity searches, and object retrievals enforce strict relational isolation (`user_id == current_user.id` or `merchant_id == current_user.merchant_id`).
3. **Role-Based Access Control (RBAC):** Administrative routes (e.g. policy ingestion, global audit streams) are guarded by `@require_role(MERCHANT_ADMIN)` or `@require_role(PLATFORM_ADMIN)`.
4. **Session Blocklisting & Invalidation:** JWTs contain unique `jti` claims. Logging out immediately persists the `jti` into an active blocklist, neutralizing replay attacks.
5. **RFC 6238 TOTP Multi-Factor Authentication:** High-privilege administrative actions and sensitive workflows support time-based one-time passwords.
6. **Cryptographic Webhook Verification:** Incoming PayPal webhooks are verified using PayPal public certificates, RSA-SHA256 signature verification, and payload CRC32 hashing.
7. **Magic-Byte Upload Validation:** Dispute evidence uploads are inspected at the binary level (magic-byte headers) to reject malicious executables masquerading as PNG, JPEG, or PDF files.
8. **Dual-Phase Read-Back Verification:** Mutations are never assumed successful based on preliminary HTTP return codes. PayPath issues an independent `GET` read-back to PayPal to verify true settlement before committing transaction state.
9. **Fail-Closed Storage Architecture:** Storage operations fail closed with HTTP 502/403. In production environments, unauthenticated local disk fallbacks are disabled.
10. **Human Approval Thresholds:** Financial actions exceeding designated risk or amount thresholds require authenticated human approval.
11. **Append-Only Immutable Audit Log:** All events, decisions, agent traces, and financial mutations are recorded with correlation IDs and timestamps.

---

## 7. Running Locally

### Prerequisites
- **Python:** 3.12.10 or compatible
- **Node.js:** 20.x or newer (with npm)
- **PostgreSQL:** 16.x running locally on `localhost:5432`

### 1. Clone the Repository
```bash
git clone https://github.com/Aryank52/Paypath.git
cd Paypath
```

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv

# On Windows PowerShell:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables (copy example and edit)
cp .env.example .env

# Run database migrations to head
alembic upgrade head

# Seed initial demonstration data
python -m backend.scripts.seed --action=seed

# Start the FastAPI development server
$env:PYTHONPATH="backend"  # PowerShell
# export PYTHONPATH="backend"  # Linux/macOS
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`.
- Health check: `http://127.0.0.1:8000/health`
- Interactive Swagger docs: `http://127.0.0.1:8000/api/v1/docs`

### 3. Frontend Setup
```bash
# In a separate terminal window
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```
Open your browser to `http://localhost:5173`. Sign in with your configured account.

### 4. Running Automated Tests
```bash
# Run backend test suite (53 tests including security and policy suites)
.venv\Scripts\python -m pytest backend/tests -v

# Run frontend build check
cd frontend
npm run build
```

---

## 8. Environment Variables

All configuration is managed through environment variables. Use `.env.example` as a template:

| Variable Name | Required | Default / Example | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Environment mode (`development`, `testing`, `production`) |
| `APP_NAME` | No | `PayPath` | Application display name |
| `API_V1_STR` | No | `/api/v1` | URL prefix for API version 1 endpoints |
| `SECRET_KEY` | Yes | `(secure-random-string)` | Secret key for signing JWT authentication tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | JWT expiration duration in minutes (24 hours) |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://postgres:postgres@localhost:5432/paypath` | SQLAlchemy async connection string for PostgreSQL |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL for caching and rate limiting |
| `PAYPAL_CLIENT_ID` | Sandbox | `(sandbox-client-id)` | PayPal REST API OAuth2 client ID |
| `PAYPAL_CLIENT_SECRET` | Sandbox | `(sandbox-client-secret)` | PayPal REST API OAuth2 client secret |
| `PAYPAL_BASE_URL` | No | `https://api-m.sandbox.paypal.com` | PayPal REST API endpoint (Sandbox or Production) |
| `PAYPAL_WEBHOOK_ID` | Sandbox | `(webhook-id)` | Registered PayPal webhook ID for signature checks |
| `SUPABASE_URL` | No | `https://<project-ref>.supabase.co` | Supabase project URL for private evidence storage |
| `SUPABASE_KEY` | No | `sb_secret_...` | Supabase server-side secret key (bypasses RLS) |
| `SUPABASE_STORAGE_BUCKET`| No | `paypath-evidence` | Name of private storage bucket for uploaded evidence |
| `GEMINI_API_KEY` | No | `(api-key)` | Optional Google Gemini API key for live AI intent parsing |
| `LLM_PROVIDER` | No | `gemini` | LLM provider identifier (`gemini` or `mock`) |
| `LLM_MODEL` | No | `gemini-2.5-flash` | Gemini model identifier |
| `ENABLE_SHOPPING` | No | `true` | Feature flag for the shopping agent subsystem |
| `ENABLE_RECOVERY` | No | `true` | Feature flag for duplicate & subscription intelligence |
| `ENABLE_RECLAIM` | No | `true` | Feature flag for the RECLAIM dispute subsystem |

> [!CAUTION]
> Never commit real secrets, API keys, or database passwords to version control. The repository `.gitignore` strictly excludes `.env`.

---

## 9. Production Status & Release Verification

**Current Release:** `v1.0.7`  
**Current Release Status:** **Production-Oriented Prototype / Release Candidate (14 of 16 Verification Gates PASS)**

PayPath is engineered and deployed as an enterprise-grade prototype / release candidate. All internal application layers—FastAPI backend services, React 19 frontend, Render Managed PostgreSQL 16 database, multi-tenant RBAC, deterministic payment policies, XGBoost risk models, and pgvector RAG—are **100% verified and operational**.

### Verification Gate Summary

| Subsystem Gate | Status | Evidence / Verification Method |
|---|---|---|
| **Gate 1: Authoritative Database** | ✅ PASS | Render PostgreSQL 16.15: Exactly 20 tables, 399 authoritative rows verified via live telemetry |
| **Gate 2: Database Schema & Migrations**| ✅ PASS | Schema initialized via SQLAlchemy async `create_all()`; repository Alembic migration head `82098dca4be4` |
| **Gate 3: Multi-Tenant RBAC** | ✅ PASS | Strict tenant isolation verified across `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` |
| **Gate 4: Authentication & Security** | ✅ PASS | JWT authentication, JTI revocation, and TOTP MFA verified |
| **Gate 5: AG Grid Explorer UI** | ✅ PASS | 0 console errors, 0 AG Grid errors on live Vercel deployment |
| **Gate 6: AI Intent Extraction** | ✅ PASS | Structured Pydantic constraint parsing verified |
| **Gate 7: Deterministic Payment Guard**| ✅ PASS | Hard rule engine (`ALLOW`, `REVIEW`, `BLOCK`, `ESCALATE`) verified |
| **Gate 8: Recovery Intelligence** | ✅ PASS | Duplicate detection and subscription waste analysis operational |
| **Gate 9: RECLAIM Dispute Subsystem** | ✅ PASS | Full dispute lifecycle, policy matching, and refund proposals verified |
| **Gate 10: Merchant Policy Studio** | ✅ PASS | Multi-merchant document ingestion and retrieval verified |
| **Gate 11: Tenant-Isolated RAG** | ✅ PASS | `pgvector` similarity search with strict `tenant_id` filtering verified |
| **Gate 12: Leakage-Free ML** | ✅ PASS | XGBoost 3.4.1 + Isolation Forest 12-feature model operational |
| **Gate 13: Multi-Agent Bus** | ✅ PASS | 7 specialized agents communicating via typed Pydantic bus verified |
| **Gate 14: Automated Test Suite** | ✅ PASS | 53 of 53 tests passing (0 failures) |
| **Gate 15: Supabase Evidence Storage** | ⚠️ BLOCKED | Private Supabase Storage is implemented with fail-closed behavior; final hosted server-side credential verification remains pending. |
| **Gate 16: PayPal Sandbox Capture E2E**| ⚠️ BLOCKED | PayPal Sandbox integration is implemented and verified through order creation, OAuth2, webhook verification, idempotency, and read-back logic. End-to-end capture remains subject to interactive Sandbox buyer approval. |

---

## 10. License

This project is licensed under the terms of the [MIT License](LICENSE).
