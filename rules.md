# PayPath — Engineering Constitution & Rules

## 1. Absolute Financial Integrity
1. **PayPal Sandbox Only:** Never run transactions against live real-money environments in development or hackathon demos.
2. **Never Expose Secrets:** `PAYPAL_CLIENT_SECRET`, JWT keys, and database passwords must never be committed to Git or sent to client-side code.
3. **Truth Comes from Backend & PayPal:** Financial state (balances, transaction status, captured amounts) is derived strictly from PayPal and the authoritative database. The AI model has zero authority to declare financial facts.
4. **AI Cannot Bypass Policy:** Every proposal emitted by an AI agent must pass through the deterministic `PolicyEngine`.
5. **Consequential Actions Require Configured Approval:** Financial operations above policy thresholds strictly require explicit human approval (`USER_APPROVAL` or `MERCHANT_APPROVAL`).
6. **Every Mutation is Idempotent:** Repeated calls with the same idempotency key must never create duplicate orders, captures, or refunds.
7. **Independent Verification is Mandatory:** Do not rely on PayPal mutation response alone. A secondary read-back of the PayPal resource must confirm the mutation before declaring `VERIFIED`.

## 2. Agentic & AI Principles
8. **Structured JSON Output Only:** LLMs must return validated JSON matching strict Pydantic schemas. Free-form text parsing for control flow is prohibited.
9. **No Fabricated Entities:** AI must never invent transaction IDs, refund amounts, or merchant names.
10. **Explainability Over Obscurity:** Every AI recommendation must include structured reasoning, cited policy clauses, and evidence summaries. Internal raw chains-of-thought are never exposed to the user.
11. **Untrusted Evidence & Policies:** User-uploaded documents and merchant policy texts are treated as untrusted data. They must never directly invoke tools or override system guidelines.

## 3. Architecture & Code Quality
12. **Decoupled PayCore:** PayPal client logic must remain isolated within `app/paycore/`. Route controllers and agents must interact with PayCore via service contracts.
13. **Strict Multi-Tenancy:** Multi-tenant boundaries (`merchant_id`, `user_id`) must be enforced at the repository/database query layer.
14. **No Silent Failure:** All errors must be handled gracefully with structured RFC-7807 problem details or clean JSON error models.
15. **No Decorative Sponsor Tech:** Every sponsor integration (PayPal, AG Grid, Render, Postman, Channel3, Elastic, Bryntum, APIMatic) must serve a concrete, functional purpose within the platform.
16. **No Breaking Regressions:** Do not break or remove existing functional capabilities when introducing new features.
17. **Continuous Documentation Sync:** Whenever models, APIs, or architectural flows change, update the corresponding documentation files in `docs/` and `tasks.md`.
