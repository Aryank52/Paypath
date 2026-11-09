# PayPath — API Specification (REST & WebSocket)

## 1. Global Standards
- **Base URL:** `/api/v1`
- **Authentication:** Bearer JWT in `Authorization` header or Secure HttpOnly cookie.
- **Idempotency:** Mutating endpoints require `X-Idempotency-Key: <UUID>`.
- **Error Format:** Standardized JSON error response:
```json
{
  "error": {
    "code": "POLICY_VIOLATION",
    "message": "Transaction exceeds configured budget limit ($100.00).",
    "request_id": "req_84f93a10",
    "details": { "budget": 100.00, "requested": 125.00 }
  }
}
```

---

## 2. Endpoints by Domain

### Authentication (`/auth`)
- `POST /auth/register` — Create user or merchant account.
- `POST /auth/login` — Authenticate and issue session tokens.
- `GET /auth/me` — Retrieve current authenticated session and permissions.
- `POST /auth/logout` — Revoke active token/session.

### Transactions (`/transactions`)
- `GET /transactions` — List transactions (supports pagination, filtering by merchant, status, risk).
- `GET /transactions/{id}` — Get detailed transaction with full event timeline and risk breakdown.
- `GET /transactions/{id}/events` — Append-only chronological lifecycle log.

### PayCore (`/paycore`)
- `POST /paycore/orders/create` — Initialize PayPal Sandbox Order with Guard check.
- `POST /paycore/orders/{id}/capture` — Authorize & capture payment; triggers independent verification.
- `POST /paycore/refunds` — Propose & execute refund for captured transaction.
- `GET /paycore/verify/{resource_id}` — Trigger independent PayPal read-back audit.
- `POST /paycore/webhooks/paypal` — Ingest and verify PayPal webhook events.

### Intent & Shopping (`/intent`, `/shop`)
- `POST /intent/parse` — Parse natural language intent into structured parameters.
- `GET /shop/search` — Query catalog for intent-matched products.
- `POST /shop/propose-purchase` — Generate payment proposal subjected to Guard evaluation.

### Policies & RAG (`/policies`)
- `POST /policies/upload` — Upload merchant policy document (.pdf, .txt, .md).
- `GET /policies/{merchant_id}` — List active policies and versions.
- `POST /policies/query` — RAG vector search across merchant policy chunks.

### RECLAIM Resolution (`/reclaim`)
- `POST /reclaim/cases` — Open new dispute / refund request for transaction.
- `POST /reclaim/cases/{id}/evidence` — Upload evidence file (image, receipt) and trigger EvidenceAgent analysis.
- `POST /reclaim/cases/{id}/evaluate` — Trigger Policy & Resolution agents for recommendation.
- `POST /reclaim/cases/{id}/approve` — Human approval gate to trigger PayPal refund execution.

### Payment Guard (`/guard`)
- `GET /guard/policies` — Retrieve active user spend policies and approval thresholds.
- `POST /guard/policies` — Update spend rules (e.g. max per-transaction, categories).
- `POST /guard/simulate` — Dry-run evaluate an arbitrary transaction payload.

### Recovery Intelligence (`/recover`)
- `GET /recover/duplicates` — Fetch suspected duplicate transactions.
- `GET /recover/subscriptions` — Fetch detected recurring payments and upcoming renewals.

