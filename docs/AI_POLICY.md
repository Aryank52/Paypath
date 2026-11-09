# PayPath — AI Policy & Governance Framework

## 1. Governance Charter
In PayPath, artificial intelligence operates strictly as an **analytical, interpretive, and propositional engine**, never as an autonomous financial authority.

```text
       ┌────────────────────────┐
       │     AI PROPOSAL        │  (Suggests intent, analysis, actions)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  DETERMINISTIC ENGINE  │  (Verifies boundaries, math, thresholds)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   HUMAN-IN-THE-LOOP    │  (Authorizes consequential financial moves)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │    PAYCORE & PAYPAL    │  (Executes transaction in sandbox)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ INDEPENDENT VERIFY     │  (Reads back authoritative state)
       └────────────────────────┘
```

---

## 2. Permitted AI Actions vs. Prohibited AI Actions

### Permitted AI Actions (Analytical & Advisory)
- Natural language classification and entity extraction.
- Product search, filtering, and comparison against stated user preferences.
- Multimodal damage assessment from product photos.
- Semantic retrieval and clause summarization from merchant policies.
- Anomaly scoring and risk explanation generation.
- Proposing candidate refund amounts bounded by transaction history.

### Prohibited AI Actions (Autonomous Financial Mutation)
- Generating or fabricating PayPal Transaction IDs, Order IDs, or Capture IDs.
- Creating arbitrary payment or refund mutations without passing through the deterministic policy engine.
- Bypassing user or merchant approval gates.
- Decreasing or increasing account balances directly in the database.
- Declaring a financial mutation "Completed" or "Verified" without an authoritative PayPal read-back confirmation.

---

## 3. Confidence & Explainability Standards
1. **Confidence is Not Authority:** A 99% confidence score from the Resolution Agent does not waive the requirement for human approval if the policy threshold requires it.
2. **Transparent Citations:** Every resolution proposal must link directly to the specific policy document, version, and section that justifies it.
3. **No Hidden Chain-of-Thought:** User-facing responses must provide clear, concise rationale without dumping internal prompt mechanics or unformatted system traces.

