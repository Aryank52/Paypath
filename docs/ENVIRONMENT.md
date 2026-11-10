# PayPath — Environment Configuration & Deployment Specification

**Document Version:** 2.0 (Phase 19 Production Certification)  
**Date:** November 2026  
**System Motto:** *Understand. Decide. Act. Verify.*  

---

## 1. Overview & Deployment Philosophy

PayPath follows a strict three-tier environment architecture: **Local Development**, **Staging / QA**, and **Production High-Assurance**. 

All environments enforce:
* Explicit secret isolation (zero hardcoded credentials; `.env` strictly untracked).
* Single authoritative PostgreSQL system of record.
* AI recommendations treated strictly as **advisory** signals, with **Deterministic Policy Engine** enforcement.
* Dual-phase independent verification on all financial operations.

---

## 2. Environment Comparison Matrix

| Configuration Dimension | Local Development | Staging / QA | Production High-Assurance |
| :--- | :--- | :--- | :--- |
| **`APP_ENV`** | `development` / `test` | `staging` | `production` |
| **Debug Mode** | `False` (Explicit JSON errors) | `False` | `False` |
| **Database Engine** | Local PostgreSQL 16 (127.0.0.1:5432) | Managed Cloud PostgreSQL 16 (SSL) | High-Availability Managed PostgreSQL 16 (SSL + Automated Backups) |
| **CORS Origins** | `http://localhost:5173`, `http://127.0.0.1:5173` | `https://staging.paypath.finance` | `https://app.paypath.finance` (No localhost) |
| **HTTPS / HSTS** | Optional / Self-signed | Enforced via Edge Proxy / Ingress | Enforced (`max-age=31536000; includeSubDomains`) |
| **Content Security Policy** | Active (Localhost connect-src permitted) | Strict (Staging host whitelist) | Strict (`default-src 'self'`, no wildcards, PayPal domains only) |
| **PayPal Gateway** | Sandbox API (`api-m.sandbox.paypal.com`) | Sandbox API (`api-m.sandbox.paypal.com`) | Live Production API (`api-m.paypal.com`) |
| **LLM Provider** | `gemini` (`gemini-2.5-flash`) / Mock fallback | `gemini` (`gemini-2.5-flash`) | `gemini` (`gemini-2.5-flash`) with quota alerting |
| **Rate Limiting** | In-Memory Sliding Window | In-Memory or Distributed Redis | Distributed Redis Token Bucket (`REDIS_URL`) |
| **Static Assets & Uploads** | Local Disk (`backend/app/uploads/`) | Private Volume Mount / Cloud Storage | Encrypted Private Object Storage with 10MB ceiling & magic bytes |
| **Webhooks Ingestion** | Local test harness / ngrok | PayPal Sandbox Webhook | Verified PayPal Production Webhook with signature validation |
| **Audit & Logging** | PostgreSQL `audit_logs` + Console JSON | PostgreSQL `audit_logs` + Aggregated ELK | PostgreSQL `audit_logs` + Immutable WORM/SIEM replication |

---

## 3. Tiered Environment Specifications

### 3.1 Local Development Environment
* **Purpose:** Feature development, adversarial testing, UI refinement, and sub-second feedback loops.
* **Database:** Native PostgreSQL 16.15 service running on port 5432 (`127.0.0.1:5432`).
* **Credentials:** Maintained locally in untracked `.env`. Zero secrets committed to source control.
* **Startup:** `.\scripts\dev-start.ps1` boots PostgreSQL check, backend on port 8000, and Vite frontend on port 5173.
* **Shutdown:** `.\scripts\dev-stop.ps1` safely terminates project ports.

### 3.2 Staging / QA Environment
* **Purpose:** Integration drills with external PayPal Sandbox and Google Gemini APIs under simulated production traffic.
* **Database:** Isolated PostgreSQL 16 staging instance. Staging migrations executed automatically via Alembic.
* **CORS:** Bound strictly to staging domain (`ALLOWED_ORIGINS=https://staging.paypath.finance`).
* **Test Strategy:** Runs end-to-end multi-agent disputes and payment capture lifecycles.

### 3.3 Production Environment
* **Purpose:** High-assurance fintech runtime handling live transactions and merchant policy compliance.
* **Database:** Multi-AZ Managed PostgreSQL 16 with point-in-time recovery (PITR) and automated daily snapshots.
* **Security & Invariants:**
  1. `DEBUG=False` strictly enforced.
  2. CORS locked down to authenticated frontend domain (`https://app.paypath.finance`). Wildcard `*` rejected at boot.
  3. `Strict-Transport-Security` and comprehensive CSP headers injected on all HTTP responses.
  4. Passwords hashed using salted `bcrypt` (12 rounds).
  5. Multi-factor authentication (TOTP) available for all administrative accounts.
  6. Rate limiting backed by high-availability Redis cluster to mitigate brute-force and DDoS vectors.
  7. Zero unhandled stack traces emitted to client consumers.

---

## 4. Environment Variables Reference (Sanitized)

```env
# Application Runtime
APP_ENV=production
APP_NAME=PayPath
API_V1_STR=/api/v1
SECRET_KEY=<GENERATE_64_CHAR_HEX_KEY>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Authoritative Database (PostgreSQL 16)
DATABASE_URL=postgresql+asyncpg://<db_user>:<db_password>@<db_host>:5432/paypath?ssl=require

# External Gateway (PayPal)
PAYPAL_MODE=production
PAYPAL_BASE_URL=https://api-m.paypal.com
PAYPAL_CLIENT_ID=<PRODUCTION_PAYPAL_CLIENT_ID>
PAYPAL_CLIENT_SECRET=<PRODUCTION_PAYPAL_CLIENT_SECRET>
PAYPAL_WEBHOOK_ID=<PRODUCTION_WEBHOOK_ID>

# AI & LLM Engine (Google Gemini)
GEMINI_API_KEY=<PRODUCTION_GEMINI_API_KEY>
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# Distributed Caching & Rate Limiting (Optional in Local, Recommended in Prod)
REDIS_URL=redis://:<redis_password>@<redis_host>:6379/0

# Network & CORS
ALLOWED_ORIGINS=https://app.paypath.finance
```

---

## 5. Security & Invariant Checklist

* [x] No plaintext secrets or passwords in configuration files or Git history.
* [x] Database URL enforces asyncpg driver and SSL encryption in production.
* [x] Policy engine decisions take precedence over LLM/ML advisory recommendations.
* [x] Secondary read-back verification mandatory before finalizing financial transaction states.
* [x] All file uploads validated against binary magic bytes (JPEG, PNG, WEBP, PDF) with 10MB limit.
