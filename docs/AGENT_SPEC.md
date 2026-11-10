# PayPath — Agent Specification & Multi-Agent Protocol

## 1. Architecture Overview
Rather than relying on a monolithic prompt, PayPath decomposes commerce and payment workflows into specialized micro-agents communicating over a strongly-typed message bus.

---

## 2. Agent Catalog & Responsibilities

The codebase implements **7 Specialized Micro-Agents** coordinated by the **AgentOrchestrator** (`backend/app/agents/`):

| Agent Name | Source File | Primary Responsibility | Input Schema | Output Schema | Permitted Tools |
|---|---|---|---|---|---|
| **IntentAgent** | `intent_agent.py` | Parse natural language into structured purchasing/guard intent | `IntentParseRequest` | `StructuredIntent` | None |
| **ShoppingAgent** | `shopping_agent.py` | Search & recommend products adhering to budget constraints | `ProductSearchRequest` | `ProductRecommendation` | `search_catalog`, `compare_items` |
| **PolicyAgent** | `policy_agent.py` | Retrieve relevant merchant policy clauses with citations | `PolicyQueryRequest` | `PolicyCitations` | `search_policy_chunks` |
| **EvidenceAgent** | `evidence_agent.py` | Analyze uploaded images/receipts for damage classification | `EvidencePayload` | `EvidenceAnalysisResult` | `vision_classify_damage` |
| **RiskAgent** | `risk_agent.py` | Detect anomalies, duplicate charges, and velocity spikes | `RiskEvaluationRequest`| `RiskScoreResult` | `scan_historical_transactions`|
| **ResolutionAgent** | `resolution_agent.py` | Formulate resolution proposal (Refund, Partial, Replace) | `ResolutionRequest` | `ResolutionProposal` | None (pure reasoning over context) |
| **VerificationAgent**| `verification_agent.py`| Query PayPal post-action to independently confirm mutation | `VerificationRequest` | `VerificationResult` | `read_paypal_resource` |
| **AgentOrchestrator**| `orchestrator.py` | Coordinates multi-agent commerce and RECLAIM workflows | `WorkflowRequest` | `WorkflowResult` | Agent dispatch & consensus |

*(Note: Transaction persistence, notification dispatch, and merchant onboarding are performed by domain service layers `TransactionService`, `NotificationService`, and `MerchantService`.)*

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

