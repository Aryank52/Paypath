# PayPath — Hackathon Demo Script & Narrative

## 1. Demo Hook (0:00 - 0:30)
> *"Modern AI agents can search the web and talk about products, but when it comes to spending real money or resolving broken purchases, people are terrified of letting AI run wild. Meet **PayPath**: The AI Transaction Intelligence, Agentic Commerce, and Payment Action Platform. PayPath turns PayPal transactions into intelligent, explainable, policy-controlled financial workflows."*

---

## 2. Step 1: Guarded Agentic Commerce (0:30 - 1:15)
1. **User Prompt:** In the PayPath AI Command Center, type:
   > *"Find travel wireless noise-cancelling headphones under $100."*
2. **Intent & Shopping:** Watch the Intent Agent extract the constraints (category: audio, budget: $100.00, approval_required: true).
3. **Product Discovery:** Shopping Agent returns the **NovaSound ANC Pro ($89.00)** from Nova Electronics.
4. **Payment Guard Check:** Payment Guard evaluates the purchase proposal:
   - Budget Check: $89.00 <= $100.00 limit (PASS)
   - Merchant Trust Score: 98% (PASS)
   - Decision: `ALLOW (Requires Human Approval)`
5. **PayPal Sandbox Execution:** User clicks "Authorize Payment". PayPath triggers PayCore to create and capture the PayPal order.
6. **Transaction Ingestion:** Transaction instantly appears in the **AG Grid Transaction Explorer** with an AI-generated health insight.

---

## 3. Step 2: Post-Purchase Issue & RECLAIM Engine (1:15 - 2:30)
1. **The Problem:** 14 days later, the package arrives, but the plastic headband is cracked.
2. **Open RECLAIM Center:** Click "Report Issue" on the Nova Electronics transaction.
3. **Upload Evidence:** Drag and drop photo of the broken headphone headband.
4. **Agent Orchestration in Action:**
   - **Evidence Agent** inspects the image: *"Physical damage detected: cracked headband (Confidence: 94%)"*.
   - **Policy Agent** runs RAG on Nova Electronics' indexed policy: cites *"Section: Damaged Goods — eligible for 75% partial refund or replacement if reported within 30 days"*.
   - **Resolution Agent** proposes: **Partial Refund of $65.00**.
   - **Policy Engine** deterministically approves the proposal within the merchant's configured parameters.
5. **Human Approval Gate:** User clicks **"Approve $65.00 Refund"**.
6. **PayPal Mutation:** PayCore dispatches an idempotent refund request to PayPal Sandbox API.
7. **Independent Verification:** The Verification Agent performs a secondary read-back to verify PayPal's authoritative ledger.
8. **Final State:** Case updates to **RESOLVED** with an immutable badge: **"Verified by PayPal"** and a complete audit trail.

---

## 4. Closing Statement (2:30 - 3:00)
> *"PayPath solves the trust problem in agentic commerce: AI understands what you want, policy controls what is allowed, humans authorize financial moves, PayPal executes the transaction, and PayPath independently verifies what happened. Understand. Decide. Act. Verify."*
