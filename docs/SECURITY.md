# PayPath — Security Architecture & Threat Model

## 1. Security Core Principles
1. **Zero Secret Leakage:** PayPal Client Secret, webhook keys, database passwords, and JWT secret keys reside strictly in backend environment variables. The frontend bundle never receives API secrets.
2. **Defensive AI Engineering:** AI agents operate under least privilege. They cannot directly execute financial mutations or modify database records without going through deterministic validation gates.
3. **Dual-Phase Mutation Verification:** To prevent optimistic UI updates and state divergence, every capture and refund is re-verified by querying PayPal directly.

---

## 2. Authentication & Session Management
- **Password Hashing:** Passwords hashed using bcrypt / Argon2id with work factor >= 12.
- **Tokens:** Short-lived JWT access tokens (15-minute expiry) paired with server-side revocable session tokens stored with HttpOnly, SameSite=Lax/Strict, and Secure flags in production.
- **Tenant Isolation:** Every protected resource checks tenant ownership (`user_id` or `merchant_id`). Direct object reference (IDOR) attacks are blocked at the repository layer.

---

## 3. Financial Safety & Idempotency
- **Idempotency Vault:** Every mutation endpoint requires `X-Idempotency-Key`. PayPath stores `idempotency_key` along with hashed request parameters and response payloads in `payment_actions`. Replayed requests return the exact previous response without hitting PayPal twice.
- **Amount Boundary Enforcement:** Refund amounts cannot be negative or exceed `captured_amount - sum(previous_refunds)`.
- **Approval Gateways:** Financial mutations exceeding policy thresholds (e.g. >$50.00) strictly transition to `AWAITING_APPROVAL` and cannot execute until an authorized user provides cryptographic or authenticated approval.

---

## 4. AI & RAG Security
- **Prompt Injection Defense:** Untrusted inputs (user descriptions, uploaded merchant policies, image text) are framed within isolated tags with explicit instructions that text inside quotes or documents cannot grant permissions or invoke tools.
- **Output Schema Validation:** All model outputs must validate against strict Pydantic models. Any malformed output is rejected and retried or escalated to human review.
- **Cross-Merchant RAG Leakage:** Vector searches filter strictly by `merchant_id` in the SQL/pgvector WHERE clause.

---

## 5. Webhook Security
- PayPal webhooks are verified using PayPal's documented signature verification API (`/v1/notifications/verify-webhook-signature`) or cert chain validation.
- Unverified webhook payloads are immediately rejected and logged.
