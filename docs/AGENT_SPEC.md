# PayPath — Agent Specification & Multi-Agent Protocol

## 1. Architecture Overview
Rather than relying on a monolithic prompt, PayPath decomposes commerce and payment workflows into specialized micro-agents communicating over a strongly-typed message bus.

---

## 2. Agent Catalog & Responsibilities

| Agent Name | Primary Responsibility | Input Schema | Output Schema | Permitted Tools |
|---|---|---|---|---|
| **IntentAgent** | Parse user natural language into structured purchasing/guard intent | `IntentParseRequest` | `StructuredIntent` | None |
| **TransactionAgent** | Ingest & normalize PayPal records, build event timelines | `RawTransactionPayload` | `NormalizedTransaction` | `query_transactions`, `lookup_paypal` |
| **ShoppingAgent** | Search & recommend products adhering to budget constraints | `ProductSearchRequest` | `ProductRecommendation` | `search_catalog`, `compare_items` |
| **PolicyAgent** | Retrieve relevant merchant policy clauses with citations | `PolicyQueryRequest` | `PolicyCitations` | `search_policy_chunks` |
| **EvidenceAgent** | Analyze uploaded images/receipts for damage classification | `EvidencePayload` | `EvidenceAnalysisResult` | `vision_classify_damage` |
| **RiskAgent** | Detect anomalies, duplicate charges, and velocity spikes | `RiskEvaluationRequest`| `RiskScoreResult` | `scan_historical_transactions`|
| **ResolutionAgent** | Formulate resolution proposal (Refund, Partial, Replace) | `ResolutionRequest` | `ResolutionProposal` | None (pure reasoning over context) |
| **VerificationAgent**| Query PayPal post-action to independently confirm mutation | `VerificationRequest` | `VerificationResult` | `read_paypal_resource` |
| **NotificationAgent**| Dispatch in-app alerts and notifications on milestones | `NotificationRequest` | `NotificationReceipt` | `emit_notification` |
| **MerchantAgent** | Ingest, chunk, and maintain merchant rules and profiles | `MerchantOnboardRequest`| `MerchantProfile` | `index_policy_document` |

---

## 3. Typed Message Bus Protocol
Agents exchange structured JSON payloads validated by Pydantic:
```json
{
  "message_id": "msg_90a1f4b2",
  "correlation_id": "corr_39a8c012",
  "from_agent": "ResolutionAgent",
  "to_agent": "PolicyEngine",
  "message_type": "ACTION_PROPOSAL",
  "timestamp": "2026-11-09T20:16:00Z",
  "payload": {
    "transaction_id": "tx_49201a",
    "case_id": "rc_8192a",
    "action": "PARTIAL_REFUND",
    "amount": 65.00,
    "currency": "USD",
    "rationale": "Item arrived with cracked plastic headband. Within 30-day window.",
    "evidence_confidence": 0.94,
    "cited_sections": ["Damaged Goods & Transit Defects"]
  }
}
```

---

## 4. Execution Limits & Safety Guards
- `MAX_AGENT_TURNS`: 8 turns maximum per workflow.
- `EXECUTION_TIMEOUT_SECONDS`: 25 seconds per orchestrator run.
- Zero unrestricted tools: Tools receive only read-only database views or pass mutations through the `PolicyEngine`.
