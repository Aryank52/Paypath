# PayPath Incident Response Playbook

## 1. Scope & Severity Classification
This document outlines standard operating procedures for security events, financial ledger discrepancies, or autonomous agent anomalies in PayPath.

| Severity | Definition | Examples | Response Target |
| :--- | :--- | :--- | :---: |
| **SEV-1 (Critical)** | Active financial loss, ledger divergence, compromised secrets | Double refund issued, PayPal credentials leaked | < 15 minutes |
| **SEV-2 (High)** | Degradation of critical policy controls, agent anomaly | Deterministic engine bypass attempt, failed independent verifications | < 1 hour |
| **SEV-3 (Medium)** | Isolated service failure, webhook delivery failures | Rate limit exhaustion, partial RAG downtime | < 4 hours |
| **SEV-4 (Low)** | Minor cosmetic or non-blocking bug | Frontend typography glitch, stale notification count | Next release |

---

## 2. Emergency Kill-Switches

### A. Disable Autonomous Agent Actions
If an agent exhibits erratic reasoning or prompt injection susceptibility:
Set `ENABLE_AGENTIC_PURCHASE=false` and `ENABLE_RECLAIM=false` in `.env` and restart backend. This forces all mutations into manual supervisor review.

### B. Revoke API Credentials & Sessions
1. Revoke PayPal Client Credentials in the PayPal Developer Dashboard.
2. Invalidate JWT session tokens by incrementing `SECRET_KEY` or restarting the token blacklist.
3. Lock compromised user accounts:
   ```sql
   UPDATE users SET is_active = false WHERE id = '<compromised_user_id>';
   ```

---

## 3. Post-Incident Reconciliation
1. **Ledger Read-Back**: Query PayPal Payments API for all captures and refunds executed within the incident window.
2. **Discrepancy Audit**: Compare PayPal ledger records against PostgreSQL `transactions` and `payment_actions`.
3. **Corrective Settlement**: Issue compensating credits or reverse misallocated adjustments through PayCore.
4. **Root Cause Analysis (RCA)**: Document incident timeline, root cause, short-term remediation, and preventative architectural controls.

