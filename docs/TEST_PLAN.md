# PayPath Comprehensive Verification & Test Plan

## Test Strategy Overview
PayPath enforces a multi-tier testing strategy covering unit tests, integration tests, security fuzzing, and end-to-end browser workflows.

```text
+-------------------------------------------------------+
|                End-to-End Verification               |
|       (FastAPI :8000 + Vite :5173 + PostgreSQL 16)    |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|            API Integration & Security Tests           |
|       (Pytest + ASGITransport + In-Memory SQLite)      |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
|                 Component Unit Tests                  |
|    (Agents, Policy Engine, PayCore Idempotency, RAG)  |
+-------------------------------------------------------+
```

## Test Suites

### 1. `test_agents.py` (4 tests)
- `test_intent_agent_extraction`: Verifies structured JSON intent classification from natural language.
- `test_policy_agent_reasoning`: Validates policy extraction and compliance reasoning.
- `test_risk_agent_anomaly_detection`: Checks duplicate detection and high-risk flags.
- `test_resolution_agent_proposal`: Verifies accurate computation of damage allowances ($65.00 cosmetic settlement on $89 headphones).

### 2. `test_api_endpoints.py` (5 tests)
- `test_health_check`: Validates `/health` returns status `HEALTHY` and database connectivity.
- `test_transactions_endpoint`: Validates `/api/v1/transactions` retrieval and schema.
- `test_intent_parsing_endpoint`: Checks `/api/v1/intent/parse` endpoint.
- `test_reclaim_lifecycle_endpoint`: Creates and queries a dispute case.
- `test_notifications_endpoint`: Validates notification fetch and mark-as-read.

### 3. `test_mfa_and_upload_security.py` (3 tests)
- `test_mfa_lifecycle`: Tests TOTP generation, clock skew tolerance, and invalid code rejection.
- `test_password_reset_flow`: Verifies reset token generation, token hashing, and password updates.
- `test_file_upload_security_magic_bytes`: Validates MIME inspection, executable blocking, and path traversal sanitization.

### 4. `test_paycore_reclaim.py` (1 test)
- `test_complete_paycore_and_reclaim_lifecycle`: End-to-end simulation of capture ➔ dispute ➔ multi-agent evaluation ➔ human approval ➔ PayPal refund ➔ independent read-back verification.

### 5. `test_policy_engine.py` (6 tests)
- Standard refund within limits (`ALLOW`).
- Refund exceeding autonomous threshold (`REVIEW`).
- Refund after return window expired (`BLOCK`).
- Damaged goods allowance calculations.
- Duplicate charge guard evaluation.
- High risk transaction escalation (`ESCALATE`).

### 6. `test_security_and_edge_cases.py` (4 tests)
- Prompt injection resilience.
- Idempotency replay attack defense (`X-Idempotency-Key`).
- Webhook signature verification and deduplication.
- Unauthorized access and invalid token handling.

