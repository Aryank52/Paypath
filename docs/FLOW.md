# PayPath — End-to-End Workflow Specifications

## 1. Hero Flow: From Intent to Verified Post-Purchase Resolution

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Client
    participant API as FastAPI Gateway
    participant Orchestrator as Agent Orchestrator
    participant Guard as Policy Engine (Guard)
    participant PayCore as PayCore Service
    participant PayPal as PayPal Sandbox API
    participant RAG as RAG Policy Engine
    participant DB as PostgreSQL 16

    Note over User, PayPal: Phase A — Pre-Purchase Intent & Guarded Execution
    User->>Frontend: "Find noise-cancelling headphones under $100 for travel"
    Frontend->>API: POST /api/v1/intent (Natural Language)
    API->>Orchestrator: Dispatch to IntentAgent
    Orchestrator->>DB: Persist Structured Intent (budget=$100, category=audio)
    Orchestrator->>Frontend: Return Recommended Product ($89.00)
    
    User->>Frontend: Click "Purchase with Guard"
    Frontend->>API: POST /api/v1/paycore/order/create
    API->>Guard: Evaluate Spend Policy ($89 <= $100 Limit)
    Guard-->>API: Decision: ALLOW (Requires Human Approval)
    API->>User: Request Final Authorization ($89.00 Nova Electronics)
    User->>API: Click "Authorize Payment"
    
    API->>PayCore: create_order(amount=89.00, currency=USD)
    PayCore->>PayPal: POST /v2/checkout/orders
    PayPal-->>PayCore: Return Order ID (e.g. 5O190127TN364715T)
    PayCore->>PayPal: POST /v2/checkout/orders/{id}/capture
    PayPal-->>PayCore: Capture Success (Capture ID: 3C498126...)
    PayCore->>PayPal: GET /v2/payments/captures/{id} (Independent Read-Back)
    PayPal-->>PayCore: Status: COMPLETED
    PayCore->>DB: Record Transaction & Event Timeline (Status: VERIFIED)
    PayCore-->>Frontend: Transaction Confirmed

    Note over User, PayPal: Phase B — Post-Purchase RECLAIM & Verified Refund
    User->>Frontend: Report Issue: "Item arrived with broken headband" + Upload Photo
    Frontend->>API: POST /api/v1/reclaim/case/create (with image file)
    API->>Orchestrator: Dispatch to EvidenceAgent & PolicyAgent
    Orchestrator->>RAG: Retrieve Nova Electronics Refund Policy (Damaged Goods)
    RAG-->>Orchestrator: Clause: "Damaged in transit eligible for 75% partial refund or replacement"
    Orchestrator->>Guard: Evaluate Resolution Proposal ($65 Partial Refund)
    Guard-->>Orchestrator: Policy Check Passed (Requires Human Approval)
    Orchestrator->>Frontend: Display Proposed Resolution ($65 Refund, Evidence Confirmed, 94% Confidence)
    
    User->>Frontend: Click "Approve $65 Refund"
    Frontend->>API: POST /api/v1/reclaim/case/{id}/approve
    API->>PayCore: execute_refund(capture_id, amount=65.00, idempotency_key)
    PayCore->>PayPal: POST /v2/payments/captures/{id}/refund
    PayPal-->>PayCore: Mutation Response (Refund ID: 7R102948...)
    PayCore->>PayPal: GET /v2/payments/refunds/{refund_id} (Independent Read-Back)
    PayPal-->>PayCore: Status: COMPLETED, Amount: 65.00 USD
    PayCore->>DB: Commit Refund & Update Case (Status: RESOLVED & VERIFIED)
    PayCore-->>Frontend: Display "Refund Verified by PayPal" Badge
```

---

## 2. Duplicate Charge Detection Flow
1. **Periodic / Ingestion Trigger:** Transaction event ingested.
2. **Deterministic Scan:** Query matches against `user_id`, `merchant_id`, `amount`, and `timestamp` within a 15-minute rolling window.
3. **Signal Generation:** If a matching transaction is found with matching external authorization characteristics, a `Potential Duplicate Signal` is generated.
4. **User Notification:** In-app alert prompts the user to review the suspected double billing.
5. **Human Control:** One-click review routes the user to RECLAIM with pre-filled duplicate evidence.

---

## 3. Policy Ingestion & Chunking Flow
1. **Merchant Upload:** Merchant uploads policy document (`.pdf`, `.md`, or `.txt`).
2. **Text Extraction:** Document parsed and normalized into structured markdown.
3. **Semantic Chunking:** Content segmented into clause-specific chunks (e.g. `Damaged Goods`, `Return Window`, `Restocking Fees`).
4. **Vector Embedding:** Chunk vectors generated via embedding provider and stored in PostgreSQL with metadata.
5. **Rule Extraction:** AI extracts candidate numerical rules (`refund_window_days: 30`, `max_auto_refund: 50.00`).
6. **Merchant Publishing:** Merchant reviews and publishes; only published versions are queried by active transactions.

