# PAYPATH — PAYPAL CAPABILITY AUDIT & DECISION MATRIX
**Document Version:** 1.0.0  
**Phase:** Master Phase 24 — PayPal Capability Audit  
**Date:** November 11, 2026  
**Environment Target:** PayPal REST v2 (Sandbox Active / Production Ready)  

---

## 1. Executive Summary

This document evaluates the complete PayPal REST API capability surface for PayPath. PayPath uses PayPal as its authoritative financial rail for order creation, settlement capture, autonomous refund execution, independent out-of-band resource verification, and cryptographically verified webhook event ingestion.

### Core Architecture Philosophy
> **"Never trust an unconfirmed client-side mutation. Verify out-of-band before state finalization."**

---

## 2. PayPal Capability Decision Matrix

| Capability / API Domain | Endpoint / Method | Integration Method | Security Invariants Enforced | Implementation Status | Technical Rationale & Architecture Alignment |
|:---|:---|:---|:---|:---|:---|
| **Orders API: Create Order** | `POST /v2/checkout/orders` | Direct REST v2 (`httpx`) | Idempotency (`PayPal-Request-Id`), currency validation, amount precision (`.2f`), audit logging | **IMPLEMENTED & VERIFIED** | Core rail for Safe Commerce checkouts. Returns `approve_url` for interactive client approval. |
| **Orders API: Show Order Details** | `GET /v2/checkout/orders/{id}` | Direct REST v2 (`httpx`) | OAuth2 Bearer token, timeout handling (15s), structured parsing | **IMPLEMENTED & VERIFIED** | Used for pre-capture verification to ensure order was approved by payer. |
| **Capture API: Capture Payment** | `POST /v2/checkout/orders/{id}/capture` | Direct REST v2 (`httpx`) | Idempotency key, dual state transition (`PENDING` -> `CAPTURED`), transaction event emission | **IMPLEMENTED & VERIFIED** | Executes financial settlement. Handles sandbox simulation fallbacks for automated testing. |
| **Authorizations API** | `POST /v2/checkout/orders/{id}/authorize` | Direct REST v2 | Two-phase commit (`AUTH` followed by manual capture) | **PREPARED & TESTED** | Supported via intent parameter (`intent: "AUTHORIZE"`). Direct capture preferred for instant commerce. |
| **Voids API** | `POST /v2/payments/authorizations/{id}/void` | Direct REST v2 | Idempotency, immediate authorization release | **PREPARED & TESTED** | Used when pre-authorization fails Payment Guard post-evaluation. |
| **Refunds API: Refund Capture** | `POST /v2/payments/captures/{id}/refund` | Direct REST v2 (`httpx`) | Deterministic policy gate, idempotency key, audit trail, state transition to `REFUNDED` | **IMPLEMENTED & VERIFIED** | Core rail for RECLAIM autonomous resolution. Only executes after policy engine validation. |
| **Refunds API: Show Refund Details** | `GET /v2/payments/refunds/{id}` | Direct REST v2 (`httpx`) | Out-of-band read-back, dual verification before updating database | **IMPLEMENTED & VERIFIED** | Independent verification step confirming PayPal refund ID, status `COMPLETED`, and amount match. |
| **Webhooks API: Signature Verification** | `POST /v1/notifications/verify-webhook-signature` & Local RSA | Dual Verification (Local RSA / API Fallback) | SSRF prevention (whitelisted PayPal cert hosts), CRC32 body check, timestamp replay protection | **IMPLEMENTED & VERIFIED** | Cryptographic verification of PayPal inbound webhooks before payload deserialization. |
| **Webhooks API: Event Ingestion** | `/api/v1/paycore/webhooks/paypal` | Inbound HTTPS Receiver | PostgreSQL deduplication (`webhook_events.event_id` UNIQUE), rate limiting (60/min), read-back verification | **IMPLEMENTED & VERIFIED** | Receives `CHECKOUT.ORDER.COMPLETED`, `PAYMENT.CAPTURE.COMPLETED`, `PAYMENT.CAPTURE.REFUNDED`. |
| **Subscriptions API** | `POST /v1/billing/subscriptions` | REST v2 Billing Engine | Cadence validation, automated monthly tracking | **ROADMAP / ADVISORY** | Handled natively by PayPath Recovery Intelligence. Recurring charge detection models subscriptions from transaction history. |
| **Transaction Search API** | `GET /v1/reporting/transactions` | Reporting REST v1/v2 | Range pagination, tenant reconciliation | **PREPARED & TESTED** | Supported via PayPath transaction reconciliation service for automated end-of-day ledger audits. |
| **Disputes API** | `GET /v1/customer/disputes` | Customer Disputes REST | Evidence attachment, auto-acceptance bounds | **INTEGRATED VIA RECLAIM** | PayPath RECLAIM acts as pre-dispute resolution layer, resolving claims before formal PayPal dispute filing. |
| **Vault API** | `POST /v3/vault/setup-tokens` | Payment Method Vaulting | PCI-DSS scoping (zero raw card storage on PayPath servers) | **PLANNED (Phase 25)** | Vaulting customer payment tokens for recurring 1-click agent commerce. |
| **Payouts API** | `POST /v1/payments/payouts` | Batch Payouts REST | Multi-party merchant disbursement | **PLANNED (Phase 25)** | For automated merchant net payout settlements after dispute hold expiration. |

---

## 3. Public Webhook Registration Status & Deployment Policy

### Explicit Engineering Directive:
> **"DO NOT register public PayPal webhooks against localhost or unverified development servers."**

1. **Current Local Status:**
   - Webhook receiver is fully implemented and cryptographically hardened in `backend/app/api/routes/webhooks.py`.
   - Comprehensive test suite in `backend/tests/test_webhooks.py` passes 100% using valid PayPal RSA signature mocks and replay attack simulations.
   - `PAYPAL_WEBHOOK_ID` is maintained as empty or sandbox-local during development.
2. **Production Registration Procedure:**
   - Public webhook creation via `POST /v1/notifications/webhooks` is strictly deferred until the Render backend deployment exposes the authoritative HTTPS endpoint:
     ```text
     https://paypath-api.onrender.com/api/v1/paycore/webhooks/paypal
     ```
   - Once public HTTPS is verified, the deployment script executes the automated registration command:
     ```bash
     python -m backend.scripts.register_paypal_webhook --url "https://paypath-api.onrender.com/api/v1/paycore/webhooks/paypal"
     ```
   - The returned `webhook_id` is then persisted into the Render production environment variables.

---

## 4. Financial Security & Reliability Guarantees

1. **Idempotency Invariant:** Every mutating request (`POST /orders`, `POST /capture`, `POST /refund`) transmits a unique `PayPal-Request-Id` UUID header. Retried network calls cannot generate duplicate authorizations or double refunds.
2. **Replay Window Enforcement:** Webhooks reject any payload with a `PAYPAL-TRANSMISSION-TIME` older than 300 seconds (5 minutes) or timestamps skewed into the future.
3. **SSRF Neutralization:** The `PAYPAL-CERT-URL` header is verified against an allowlist requiring HTTPS and the exact PayPal domain hierarchy (`api.paypal.com` or `api.sandbox.paypal.com`).
4. **Independent Read-Back:** State transitions to `VERIFIED` require a fresh `GET` call directly to PayPal's API to confirm resource status, currency, and amount.
