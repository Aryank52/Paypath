# PayPath PayPal Webhook Integration & E2E Security Certification

**Document Version:** 1.0.0  
**Registered Production Webhook Endpoint:** `https://paypath-8u9a.onrender.com/api/v1/paycore/webhooks/paypal`  
**PayPal API Environment:** Sandbox (`https://api-m.sandbox.paypal.com`)  
**Security Standard:** PayPal Webhook Signature Verification API + Persistent Replay Deduplication  

---

## 1. Executive Summary

PayPath integrates with PayPal Sandbox for real-time payment capture, order authorization, automated and merchant-mediated refunds, and asynchronous webhook lifecycle notifications.

To prevent payment tampering, forged notifications, and replay attacks, PayPath enforces:
1. **Asymmetric Cryptographic Signature Verification (RSA-SHA256):** Every incoming webhook is authenticated using PayPal's X.509 public key certificate. The verifier reconstructs the signed message `<transmission_id>|<transmission_time>|<webhook_id>|<crc32(raw_body)>` and validates the RSA PKCS#1 v1.5 signature using SHA-256. If configured, a fallback check can also cross-verify via PayPal's `/v1/notifications/verify-webhook-signature` API.
2. **Persistent PostgreSQL Replay Defense:** Transmission IDs and Event IDs are recorded in the authoritative `webhook_events` PostgreSQL 16 table (`paypal_event_id` and `transmission_id`). Duplicate transmissions receive HTTP 200 with an idempotent `{"status": "IGNORED", "reason": "DUPLICATE_EVENT"}` response without duplicate financial mutations, surviving container and service restarts.
3. **Audit Trail Recording:** Verified events are logged into PostgreSQL 16 with timestamps, event types, resource IDs, and financial delta tracking.

---

## 2. Webhook Event Processing Flow

```
PayPal Cloud
     │  POST /api/v1/paycore/webhooks/paypal
     ▼
FastAPI Route (`webhooks.py`)
     │
     ├── 1. Validate presence of all 5 required PayPal headers:
     │      - PAYPAL-AUTH-ALGO (e.g. SHA256withRSA)
     │      - PAYPAL-CERT-URL (must end with .paypal.com and start with /v1/notifications/certs/)
     │      - PAYPAL-TRANSMISSION-ID
     │      - PAYPAL-TRANSMISSION-SIG (Base64-encoded RSA signature)
     │      - PAYPAL-TRANSMISSION-TIME (validated within 30-minute timestamp window)
     │
     ├── 2. Cryptographic RSA-SHA256 Verification:
     │      - Fetch & cache X.509 PEM certificate from PayPal (or test registry in tests)
     │      - Extract RSA public key
     │      - Compute CRC32 checksum over exact raw body bytes
     │      - Format string: <transmission_id>|<transmission_time>|<webhook_id>|<crc32>
     │      - Verify RSA signature with PKCS#1 v1.5 padding and SHA-256
     │
     ├── 3. Persistent Replay & Deduplication Check (PostgreSQL 16):
     │      - Query WebhookEvent.paypal_event_id == event_id
     │      - Query WebhookEvent.transmission_id == transmission_id
     │      - If record exists in DB -> RETURN 200 {"status": "IGNORED", "reason": "DUPLICATE_..."}
     │
     ├── 4. Authoritative State Mutation (PostgreSQL 16):
     │      - Insert WebhookEvent record with status "WEBHOOK_AUTHENTICATED"
     │      - PAYMENT.CAPTURE.COMPLETED -> Update Transaction status to COMPLETED
     │      - PAYMENT.CAPTURE.DENIED -> Mark Transaction FAILED / REJECTED
     │      - PAYMENT.CAPTURE.REFUNDED -> Update Transaction refund amount, set status REFUNDED / PARTIALLY_REFUNDED
     │
     └── 5. Persist Audit Record & Dispatch Real-Time Notifications
```

---

## 3. Adversarial Test Matrix & Verification Results

PayPath includes 10 dedicated automated test scenarios in `backend/tests/test_paypal_webhook_security.py`:

| Test Name | Test Condition | Expected Response | Result |
| :--- | :--- | :--- | :--- |
| `test_webhook_missing_headers` | Headers omitted | `400 Bad Request` | **PASSED** |
| `test_webhook_invalid_cert_url` | Cert URL points to attacker domain (`evil.com`) | `400 Bad Request` | **PASSED** |
| `test_webhook_expired_timestamp` | Timestamp $> 10$ minutes old | `400 Bad Request` | **PASSED** |
| `test_webhook_invalid_signature` | Corrupted signature string | `400 Bad Request` | **PASSED** |
| `test_webhook_modified_payload` | Payload bytes tampered after signing | `400 Bad Request` | **PASSED** |
| `test_webhook_wrong_webhook_id` | Webhook ID mismatch | `400 Bad Request` | **PASSED** |
| `test_webhook_missing_event_id` | Missing `id` in JSON body | `400 Bad Request` | **PASSED** |
| `test_webhook_valid_event_and_deduplication` | Valid signature + state transition | `200 OK` (State applied) | **PASSED** |
| `test_webhook_duplicate_transmission_id` | Replay of valid event | `200 OK` (No duplicate mutation) | **PASSED** |
| `test_webhook_unknown_event_type` | Unrecognized PayPal event type | `200 OK` (Logged safely, ignored) | **PASSED** |
| `test_webhook_capture_reconciliation_mismatch` | Captured amount does not match order | `422 Unprocessable Entity` | **PASSED** |

---

## 4. Production Webhook Verification Command

To test the live webhook endpoint from any terminal:

```bash
curl -X POST "https://paypath-8u9a.onrender.com/api/v1/paycore/webhooks/paypal" \
     -H "Content-Type: application/json" \
     -d '{"test": "ping"}'
```

**Expected Production Response:**
```json
{
  "detail": "Missing required PayPal webhook headers: PAYPAL-AUTH-ALGO, PAYPAL-CERT-URL, PAYPAL-TRANSMISSION-ID, PAYPAL-TRANSMISSION-SIG, PAYPAL-TRANSMISSION-TIME"
}
```
*HTTP 400 Bad Request — Confirms fail-closed protection is actively running on Render.*

---

## 5. Live Production Webhook Audit: Real vs. Simulated

PayPath enforces strict production truthfulness regarding incoming PayPal webhooks:

- **Registered Webhook ID:** `6ES101932C8932818` (Registered on PayPal Sandbox pointing to `https://paypath-8u9a.onrender.com/api/v1/paycore/webhooks/paypal`).
- **Simulated Events Processed:**
  - `WH-58D329510W468432D-8HN650336L201105X` (`PAYMENT.CAPTURE.COMPLETED`, Capture ID `12A34567BC123456S`)
  - `WH-1GE84257G0350133W-6RW800890C634293G` (`PAYMENT.CAPTURE.REFUNDED`, Refund ID `1Y107995YT783435V`)
- **Event Classification:**
  These events were delivered by the official **PayPal Sandbox Webhook Simulator**. They verify that Render parses headers, validates certificates, and applies state mutations correctly.
- **Organic Checkout Events:**
  No real organic buyer checkout webhooks have been received on the live endpoint yet, because unattended checkout in PayPal Sandbox requires interactive human buyer approval on the PayPal Wallet interface.
- **Status:** **SIMULATED VERIFIED (Organic Pending Interactive Buyer Flow)**.


