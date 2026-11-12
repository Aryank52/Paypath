# PayPath Fallback Audit & Fail-Closed Architectural Certification

**Document Version:** 1.0.0  
**Status:** Certified & Production Verified  
**Core Invariant:** Production environments MUST fail closed. Degraded modes are permitted only in verified local/test environments or when explicitly governed by non-authoritative fallback policies.

---

## 1. Executive Summary

In financial and transactional architectures, unconstrained fallback mechanisms present severe security and auditability hazards. A fallback that silently switches from a persistent cloud database to an ephemeral in-memory database, or from secure cloud storage to an ephemeral container disk, creates catastrophic data loss and breaks regulatory audit trails.

This audit details every fallback mechanism in PayPath, certifying that:
1. Production configurations fail closed with explicit, actionable error codes (`502 Bad Gateway`, `503 Service Unavailable`, `401 Unauthorized`).
2. SQLite fallback is strictly forbidden in production and isolated to automated test suites.
3. Supabase evidence persistence fails closed in production.
4. PayPal Webhooks and payment verifications fail closed if cryptographic integrity cannot be validated.
5. AI reasoning engines are strictly advisory and bound by deterministic policy engines.

---

## 2. Systematic Audit of Subsystem Fallbacks

### 2.1 Database Layer (PostgreSQL 16 Authoritative vs. SQLite Test Harness)

- **Audited Files:** `backend/app/db/session.py`, `backend/app/core/config.py`, `backend/app/main.py`
- **Previous Hazard:** Early prototypes tolerated falling back to SQLite if PostgreSQL was unreachable.
- **Production Hardening:**
  - `backend/app/db/session.py` inspects `settings.APP_ENV`.
  - When `APP_ENV == "production"`, the database driver is strictly enforced as `postgresql+asyncpg://`.
  - If PostgreSQL 16 is unreachable or credentials fail, the application startup **fails immediately and exits with status code 1**.
  - SQLite (`sqlite+aiosqlite:///:memory:`) is strictly constrained to `APP_ENV == "test"`.
  - Render production environment uses managed PostgreSQL 16 with zero SQLite presence.
- **Certification Result:** **PASSED (Fail-Closed Enforced)**

---

### 2.2 Evidence Storage (Supabase Storage vs. Local Filesystem)

- **Audited Files:** `backend/app/core/upload_security.py`, `backend/app/services/storage_service.py`
- **Previous Hazard:** If Supabase was unconfigured or returned an error, uploads fell back to `./uploads/` on the local disk. In containerized production (Render), container restarts wipe local disks, destroying legal evidence files for open RECLAIM disputes.
- **Production Hardening:**
  - In `upload_security.py` and `storage_service.py`, environment detection checks `is_prod = settings.APP_ENV == "production"`.
  - In production, if `SUPABASE_URL` or `SUPABASE_KEY` is missing, or if Supabase upload encounters a network/API failure, the system throws `HTTPException(status_code=502, detail="Secure evidence cloud storage is temporarily unavailable. Upload could not be verified.")`.
  - Silent fallback to `./uploads/` is **strictly blocked** in production.
  - Local disk storage is permitted solely during local development and automated pytest runs.
- **Certification Result:** **PASSED (Fail-Closed Enforced)**

---

### 2.3 PayPal Webhook Verification & Order Capture

- **Audited Files:** `backend/app/services/paypal_service.py`, `backend/app/api/routes/webhooks.py`
- **Previous Hazard:** If PayPal verification service was offline, webhooks might execute transactional state changes without signature proof.
- **Production Hardening:**
  - `verify_webhook_signature()` contacts PayPal API (`/v1/notifications/verify-webhook-signature`) with the transmission ID, timestamp, webhook ID, and signature.
  - If PayPal returns `verification_status != "SUCCESS"`, or if the verification call raises an exception, the webhook route rejects the payload with `400 Bad Request` or `401 Unauthorized`.
  - Replay attacks are prevented via a persistent Redis / in-memory deduplication cache checking `(event_id, transmission_id)`.
  - Under no circumstances does PayPath mutate order capture or refund records upon an unverified webhook.
- **Certification Result:** **PASSED (Fail-Closed Enforced)**

---

### 2.4 AI Engine & Policy Determinism (Advisory LLM vs. Authoritative Policy Engine)

- **Audited Files:** `backend/app/services/guard_service.py`, `backend/app/services/reclaim_service.py`, `backend/app/services/agent_service.py`
- **Architectural Invariant:**
  > **Understand. Decide. Act. Verify.**
- **Enforcement Details:**
  - Large Language Models (Google Gemini 2.5 Flash / Pro) are categorized as **non-authoritative intelligence advisors**.
  - LLM outputs are parsed for intent, semantic risk indicators, and user sentiment.
  - However, the final transactional decision (`ALLOW`, `BLOCK`, `REQUIRE_VERIFICATION`, `AUTO_REFUND`) is executed strictly by the deterministic **Payment Guard Policy Engine** using mathematical thresholds and merchant policy rules stored in PostgreSQL.
  - If the Gemini API experiences a timeout, rate limit (429), or outage:
    - The transaction is NOT blindly approved.
    - Payment Guard defaults to deterministic heuristic scoring and flags the transaction for step-up verification if risk score $\ge 0.60$.
    - The user receives a clear status explaining that automated AI narrative generation was deferred, while core transaction protection remained active.
- **Certification Result:** **PASSED (Deterministic Authority Enforced)**

---

### 2.5 Demo Persona Authentication Fallback

- **Audited Files:** `frontend/src/components/LandingPage.tsx`, `frontend/src/components/Navbar.tsx`
- **Previous Hazard:** Frontend components previously set mock strings (e.g. `'demo-token-alex'`) in `localStorage` when clicking quick demo cards, resulting in 401 Unauthorized errors when fetching transactions.
- **Production Hardening:**
  - Removed all synthetic client-side tokens.
  - Every demo persona switch executes an authentic `POST /api/v1/auth/login` HTTP request against the FastAPI backend using authentic seeded demo credentials.
  - The returned cryptographic JWT is validated and stored in `localStorage`.
  - If the backend is unreachable, the UI surfaces a connection error banner rather than displaying a broken or fake state.
- **Certification Result:** **PASSED (Real Authentication Enforced)**

---

## 3. Fallback Compliance Matrix

| Component | Dev/Test Behavior | Production Behavior | Invariant Maintained? |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 16** | Allowed SQLite fallback in pytest | Immediate startup crash if PostgreSQL unavailable | **Yes** — zero data loss risk in prod |
| **Supabase Storage** | Local `./uploads/` filesystem | HTTP 502 error; local disk prohibited | **Yes** — dispute evidence preserved |
| **PayPal Webhooks** | Mock verification in unit tests | Strict PayPal API verification + replay check | **Yes** — spoofed events rejected |
| **Gemini AI Engine** | Mock responses in mock tests | Deterministic Policy Engine defaults to safe verification | **Yes** — AI is non-authoritative |
| **Auth Personas** | Seeded credentials via real login | Seeded credentials via real login | **Yes** — valid JWTs guaranteed |

