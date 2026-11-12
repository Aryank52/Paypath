# PayPath PayPal Webhook Integration & E2E Security Certification

**Document Version:** 1.0.0  
**Registered Production Webhook Endpoint:** `https://paypath-8u9a.onrender.com/api/v1/paycore/webhooks/paypal`  
**PayPal API Environment:** Sandbox (`https://api-m.sandbox.paypal.com`)  
**Security Standard:** PayPal Webhook Signature Verification API + Persistent Replay Deduplication  

---

## 1. Executive Summary

PayPath integrates with PayPal Sandbox for real-time payment capture, order authorization, automated and merchant-mediated refunds, and asynchronous webhook lifecycle notifications.

To prevent payment tampering, forged notifications, and replay attacks, PayPath enforces:
1. **Cryptographic Signature Verification:** Every incoming webhook is checked against PayPal's verification service using the `PAYPAL-TRANSMISSION-ID`, `PAYPAL-TRANSMISSION-TIME`, `PAYPAL-TRANSMISSION-SIG`, `PAYPAL-CERT-URL`, and configured `PAYPAL_WEBHOOK_ID`.
2. **Replay Defense:** Transmission IDs and Event IDs are recorded in an in-memory / cache deduplication store. Duplicate transmissions receive HTTP 200 with an idempotent "Already Processed" response without duplicate state mutations.
3. **Audit Trail Recording:** Verified events are logged into PostgreSQL 16 with timestamps, event types, resource IDs, and financial delta tracking.

---

## 2. Webhook Event Processing Flow

```
PayPal Cloud
     │  POST /api/v1/paycore/webhooks/paypal
     ▼
FastAPI Route (`webhooks.py`)
     │
     ├── 1. Validate presence of required headers:
     │      - PAYPAL-TRANSMISSION-ID
     │      - PAYPAL-TRANSMISSION-TIME
     │      - PAYPAL-TRANSMISSION-SIG
     │      - PAYPAL-CERT-URL
     │
     ├── 2. Verify Certificate URL Origin:
     │      - Must end with .paypal.com
     │
     ├── 3. Contact PayPal Signature Verification API:
     │      - POST /v1/notifications/verify-webhook-signature
     │      - Pass transmission parameters, webhook ID, and raw payload
     │      - If verification_status != "SUCCESS" -> REJECT (400 Bad Request)
     │
     ├── 4. Replay Check:
     │      - Key: paypal_webhook:{event_id}:{transmission_id}
     │      - If key exists in cache -> RETURN 200 {"status": "duplicate_ignored"}
     │
     ├── 5. Authoritative State Mutation (PostgreSQL 16):
     │      - PAYMENT.CAPTURE.COMPLETED -> Update Transaction status to COMPLETED
     │      - PAYMENT.CAPTURE.DENIED -> Mark Transaction FAILED / REJECTED
     │      - PAYMENT.CAPTURE.REFUNDED -> Update Transaction refund amount, set status REFUNDED / PARTIALLY_REFUNDED
     │
     └── 6. Persist Audit Record & Dispatch Real-Time Notifications
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

