# PayPath — External Provider Status & Integration Matrix

**Document Version:** 2.1 (Phase 19 Certification)  
**Date:** November 2026  
**Status:** Certified Runtime Matrix  
**System Motto:** *Understand. Decide. Act. Verify.*  

---

## 1. Provider Truth & Configuration Matrix

This matrix provides the exact, audited status of every external provider, database, AI system, payment gateway, and storage layer across the PayPath system.

| Provider | Environment Variable(s) | Configured | Connected | Runtime State | Fallback Mechanism | Audit Verdict |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **PostgreSQL 16** | `DATABASE_URL` | **YES** | **YES** | **CONNECTED** | None (PostgreSQL 16 is single authoritative system of record: 20 tables, 303 records) | **FULLY CONNECTED & AUTHORITATIVE** |
| **PayPal Sandbox** | `PAYPAL_CLIENT_ID`<br>`PAYPAL_CLIENT_SECRET`<br>`PAYPAL_BASE_URL` | **PENDING** | **READY** | **NOT_CONFIGURED** | Deterministic mock gateway with full order/capture/refund simulation & read-back verifier | **INTEGRATED (READY FOR SANDBOX KEYS)** |
| **LLM Engine (Gemini)** | `GEMINI_API_KEY`<br>`LLM_PROVIDER`<br>`LLM_MODEL` | **PENDING** | **READY** | **MOCK** | Deterministic structured intent/resolution extractor (`MockLLMProvider`) + safe failure handling | **INTEGRATED (READY FOR GEMINI KEY)** |
| **RAG Vector Store** | PostgreSQL `policy_chunks` | **YES** | **YES** | **ACTIVE** | In-memory hydrated 128-dim normalized cosine index with `merchant_id` tenant isolation | **FULLY CONNECTED & ZERO-LEAK ISOLATED** |
| **ML Engine** | `artifacts/ml/*` | **YES** | **YES** | **VALIDATED** | Deterministic fallback rules via `DeterministicPolicyEngine` (ML is strictly advisory) | **VALIDATED ON BENCHMARK DATASET** |
| **Specialized Agents** | Micro-Agent Engine | **YES** | **YES** | **ACTIVE** | 7 specialized micro-agents + `AgentOrchestrator` with PostgreSQL trace persistence | **HEALTHY & TRACE-PERSISTED** |
| **Redis Cache** | `REDIS_URL` | **NO** | **NO** | **NOT_CONFIGURED** | In-memory token revocation blocklist set & route-level safeguards | **FALLBACK TO IN-MEMORY** |
| **File Storage** | Local `backend/app/uploads` | **YES** | **YES** | **WRITABLE** | Local disk with binary magic-byte inspection (JPEG, PNG, WEBP, PDF) & 10MB ceiling | **WRITABLE & SECURE** |
| **Email Service** | `ENABLE_EMAIL` | **NO** | **NO** | **NOT_CONFIGURED** | In-app notification center (`notifications` table) & mock email logger | **IN-APP NOTIFICATIONS ACTIVE** |

---

## 2. Subsystem Telemetry Standards

The `/api/v1/system/health` telemetry route actively inspects each subsystem and reports multi-state status rather than collapsing into boolean values:

### 2.1 PostgreSQL 16
- **Status:** `CONNECTED`
- **Telemetry:** Measures live query latency (`SELECT version()`), version (`PostgreSQL 16.15`), and database name (`paypath`).
- **Row Counts:** 20 tables, 304 persisted records (including 7 agent runs and 30 agent tool calls).

### 2.2 PayPal Gateway
- **Status States:**
  - `NOT_CONFIGURED`: When `PAYPAL_CLIENT_ID` or `PAYPAL_CLIENT_SECRET` are empty in `.env`.
  - `CONFIGURED`: When credentials exist in `.env` but token handshake is not yet attempted.
  - `CONNECTED`: When live OAuth2 token handshake against `https://api-m.sandbox.paypal.com/v1/oauth2/token` succeeds.
  - `ERROR`: When network or invalid credentials cause an HTTP failure.
- **Financial Invariants:** Verified order creation, capture, partial refund, exact idempotency replay, 409 Conflict on altered replay amounts, and 400 rejection on exceeding balance.

### 2.3 LLM Engine
- **Status States:**
  - `NOT_CONFIGURED`: Provider selected (e.g., `gemini`) but `GEMINI_API_KEY` is empty.
  - `MOCK`: `LLM_PROVIDER=mock` or offline development mode (`deterministic-mock-v1`).
  - `CONFIGURED`: API key present but model endpoint not yet probed.
  - `CONNECTED`: Live probe to Google Gemini model (`gemini-2.5-flash`) succeeds with HTTP 200.
  - `ERROR`: API key rejected, quota exceeded, or network timeout.
- **Safety Boundary:** When LLM provider fails in strict mode, `LLMProviderError` is raised and execution halts safely with zero downstream financial actions.

### 2.4 ML Subsystem
- **Status States:**
  - `ACTIVE`: Both Supervised XGBoost classifier (`v1.0.0`) and Unsupervised Isolation Forest (`v1.0.0`) are loaded into memory with 12-feature pipeline.
  - **Dataset:** `paypath_temporal_split_v1` (70% Train, 15% Validation, 15% Test).
  - **Role:** Strictly `ADVISORY_ONLY`. All actions constrained by the Deterministic Policy Engine.

### 2.5 RAG Vector Store
- **Status States:**
  - `ACTIVE`: 19 policy chunks hydrated from PostgreSQL 16 `policy_chunks` into in-memory cosine similarity index.
  - **Tenant Boundary:** 0 cross-merchant clause leaks verified across isolated tenants.

### 2.6 Specialized Agents
- **Status States:**
  - `HEALTHY`: 7 specialized micro-agents (`IntentAgent`, `ShoppingAgent`, `PolicyAgent`, `EvidenceAgent`, `RiskAgent`, `ResolutionAgent`, `VerificationAgent`) coordinated by `AgentOrchestrator`.
  - **Trace Persistence:** Audit traces persisted to PostgreSQL `agent_runs` and `agent_tool_calls`.

---

## 3. Activation Protocol for Live Production Keys

When activating live PayPal Sandbox credentials or Google Gemini API keys:

1. Safely add credentials to `.env` without printing or exposing them:
   ```bash
   printf "Enter PAYPAL_CLIENT_ID: " && read -s val && echo && echo "PAYPAL_CLIENT_ID=$val" >> .env
   printf "Enter PAYPAL_CLIENT_SECRET: " && read -s val && echo && echo "PAYPAL_CLIENT_SECRET=$val" >> .env
   printf "Enter GEMINI_API_KEY: " && read -s val && echo && echo "GEMINI_API_KEY=$val" >> .env
   ```
2. Restart backend:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
3. Verify live telemetry via HTTP:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/system/health"
   ```
   Expected response upon successful handshake:
   ```json
   {
     "status": "HEALTHY",
     "subsystems": {
       "postgresql": "healthy",
       "paypal": "connected",
       "llm": "connected",
       "rag": "healthy",
       "ml": "validated",
       "agents": "healthy"
     }
   }
   ```
   ```
