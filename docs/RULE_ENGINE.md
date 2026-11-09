# PayPath Deterministic Policy Rule Engine

## Architecture & Design
The rule engine enforces absolute mathematical guarantees over financial transactions. While AI agents analyze context, reason over text, and suggest actions, **only the deterministic policy engine can grant execution authority.**

```text
               +----------------------------------+
               |   AI Agent Proposed Resolution   |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |   Deterministic Policy Engine    |
               +-----------------+----------------+
                                 |
             +-------------------+-------------------+
             |                   |                   |
             v                   v                   v
        [ ALLOW ]           [ REVIEW ]          [ BLOCK ]
     Auto-Approve       Human Gate Required   Violates Limits
```

## Policy Decision Enum
1. **`ALLOW`**: Transaction meets all thresholds (amount within autonomous limit, return window active, confidence >= 0.85).
2. **`REVIEW`**: Transaction exceeds autonomous limit or has moderate risk; requires human approval before dispatch.
3. **`BLOCK`**: Explicit violation of hard constraints (amount > merchant max refund, claim after deadline, counterfeit item).
4. **`ESCALATE`**: High anomaly or dispute requiring supervisor review.

## Rule Evaluation Flow
1. **Context Ingestion**: Gathers transaction amount, merchant ID, item category, time elapsed since delivery, and evidence analysis confidence.
2. **Constraint Verification**:
   - `ClaimAmount <= CapturedAmount`
   - `DaysElapsed <= ReturnWindowDays`
   - `RefundAmount <= MerchantMaxAutonomousLimit` (e.g. $250.00)
3. **Decision Generation**:
   - Computes allowed settlement amount based on policy percentage (e.g., cosmetic defect = 75% max or fixed credit).
   - Generates exact policy citation explaining which clause governs the outcome.

