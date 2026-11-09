# PayPath Official Sources & Platform References

## 1. PayPal Developer Platform
- **REST APIs v2 Reference**: `https://developer.paypal.com/docs/api/overview/`
- **Orders API v2**: `https://developer.paypal.com/docs/api/orders/v2/`
  - `POST /v2/checkout/orders` (Order Creation)
  - `POST /v2/checkout/orders/{id}/capture` (Payment Capture)
  - `GET /v2/checkout/orders/{id}` (Read-Back Independent Verification)
- **Payments API v2**: `https://developer.paypal.com/docs/api/payments/v2/`
  - `POST /v2/payments/captures/{id}/refund` (Idempotent Refund Dispatch)
  - `GET /v2/payments/refunds/{id}` (Refund Settlement Verification)
- **Webhooks v1**: `https://developer.paypal.com/docs/api/webhooks/v1/`
  - Webhook verification via PayPal public key certificates and event hash signatures.

## 2. Artificial Intelligence & RAG
- **Google Gemini API**: Official Google GenAI Python SDK (`google-genai`)
  - Grounding transaction evidence against merchant policy documentation.
  - Zero-hallucination guardrails: Model outputs must cite indexed policy clauses.

## 3. Data Infrastructure & Sponsors
- **PostgreSQL 16**: Authoritative ACID relational data storage with JSON vector embeddings.
- **AG Grid Community / Enterprise**: Enterprise-grade financial data grid with sorting, quick filtering, and row-level lifecycle visualization.
- **Render Cloud**: Deployment specification via `render.yaml` for FastAPI ASGI web service and managed PostgreSQL.

