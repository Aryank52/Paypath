# PayPath RECLAIM Complaint & Dispute Resolution System

## Overview
The **RECLAIM** subsystem transforms subjective, emotionally charged customer complaints into structured, objective, policy-grounded financial dispute resolutions.

```text
Customer Complaint / Damaged Goods
              ↓
Evidence Extraction (Photo/Receipt/Video OCR)
              ↓
RAG Policy Retrieval (Isolated by Merchant Tenant)
              ↓
Multi-Agent Deliberation (Risk, Policy, Resolution)
              ↓
Deterministic Policy Engine Guardrail
              ↓
Human-in-the-Loop Approval Gate
              ↓
PayPal Sandbox Execution via PayCore
              ↓
Dual-Phase Read-Back Verification & Settlement Audit
```

## Complaint Lifecycle States
1. **`OPEN`**: Dispute case registered by shopper.
2. **`EVIDENCE_REQUIRED`**: Awaiting upload of photos, receipts, or damage documentation.
3. **`UNDER_REVIEW`**: Evidence analyzed for forgery, image metadata, and damaged area classification.
4. **`AI_RECOMMENDED`**: Multi-agent consensus reached citing exact merchant policy clauses.
5. **`AWAITING_APPROVAL`**: Settlement proposal staged for human sign-off.
6. **`APPROVED`**: Authorized by user/merchant admin.
7. **`RESOLVED`**: Refund/credit executed via PayPal and verified independently.
8. **`REJECTED`**: Denied by policy or human authority with clear explanation.

## Evidence Verification Standards
- **Image Authentication**: Magic byte inspection (`JPEG`, `PNG`, `WEBP`, `PDF`).
- **Damage Severity Assessment**: Vision analysis estimates damage extent (cosmetic vs. structural).
- **Policy Cross-Referencing**: Semantic similarity search over merchant's vector index guarantees proposed amounts stay within pre-approved thresholds.
- **Audit Logging**: Every transition is immutably recorded in PostgreSQL `audit_logs`.

