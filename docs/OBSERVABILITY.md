# PayPath Observability, Metrics & Telemetry Specification

## Architecture
PayPath provides structured JSON logging, distributed trace identifiers, and real-time health telemetry across the application lifecycle.

```text
HTTP Request
     ↓
Correlation ID Middleware (X-Request-ID)
     ↓
Structured JSON Logger (Timestamp, Level, Request Path, Actor)
     ↓
Performance Timings & Database Metrics
     ↓
Prometheus / OpenTelemetry Export Format
```

## 1. Structured Logging Format
All server logs follow a standardized JSON envelope:
```json
{
  "timestamp": "2026-11-09T16:26:26.436897+00:00",
  "level": "INFO",
  "message": "PayPal payment captured successfully. Verified by PayPal read-back audit.",
  "logger": "paypath.paycore",
  "request_id": "req_8921a8f9-4102-4012-9c12",
  "actor_id": "usr_demo_shopper_01",
  "action": "PAYMENT_CAPTURED",
  "transaction_id": "tx_nova_anc_hero",
  "duration_ms": 142.5
}
```

## 2. Health & Readiness Endpoints
- **`GET /health`** & **`GET /api/v1/health`**:
  - `status`: `"HEALTHY"` or `"DEGRADED"`.
  - `database`: PostgreSQL 16 connection state (`"CONNECTED"` verified via live query).
  - `paypal_configured`: Boolean indicating sandbox credentials presence.
  - `environment`: Deployment stage (`development`, `production`).

## 3. Key Financial Metrics Monitored
1. **Mutation Verification Latency**: Time required for independent read-back query to PayPal API.
2. **Idempotency Collision Rate**: Frequency of identical `X-Idempotency-Key` replay attempts.
3. **Policy Engine Distribution**: Ratio of `ALLOW` vs. `REVIEW` vs. `BLOCK` decisions.
4. **Agent Confidence Scores**: Distribution of confidence ratings from Policy and Resolution agents.

