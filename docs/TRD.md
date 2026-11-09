# PayPath — Technical Requirements Document (TRD)

## 1. System Architecture & Component Design
PayPath is architected as a modular, decoupled full-stack platform consisting of:
1. **Frontend Client:** Single Page Application (SPA) built with React 19, TypeScript, Vite, Tailwind CSS v4, AG Grid Enterprise/Community, and Zustand.
2. **Backend API & Orchestrator:** Asynchronous Python 3.12 service powered by FastAPI, Pydantic v2, and SQLAlchemy 2.0.
3. **PayCore Subsystem:** Isolated payment engine managing PayPal REST v2 APIs, OAuth2 client credentials token rotation, idempotency enforcement, and independent read-back verification.
4. **Agent Orchestrator:** Event-driven multi-agent coordinator utilizing structured typed messaging schemas.
5. **RAG Subsystem:** Document chunking, vector embedding, and hybrid similarity search backed by PostgreSQL `pgvector`.
6. **Data Storage:** PostgreSQL 16 (authoritative store), Redis (rate limiting & task state caching).

## 2. API & Communication Protocols
- **RESTful JSON API:** OpenAPI 3.1 compliant endpoints grouped logically (/auth, /transactions, /paycore, /intent, /policies, /reclaim, /approvals, /audit).
- **Idempotency:** HTTP Header `X-Idempotency-Key` enforced on all POST/PUT financial mutations.
- **Agent Communication:** In-memory typed bus dispatching validated Pydantic models between specialized agents.

## 3. Data Integrity & Financial State Transitions
- Transactions and payment actions must follow strict state machines.
- A financial mutation (`REFUND` or `CAPTURE`) is never marked complete based solely on the immediate mutation response. A secondary verification step queries the PayPal resource directly to confirm that `status == 'COMPLETED'`, `amount` matches, and `currency` matches.
- All financial operations write immutable records to the `audit_logs` table with request ID, actor, timestamp, and before/after payloads.

## 4. Multi-Tenant Isolation
- Merchants and users are isolated via composite tenant keys (`merchant_id`, `user_id`).
- All database queries and vector similarity searches strictly filter by tenant scope.

## 5. Fallback & Fault Tolerance
- **PayPal Sandbox:** Mock adapter available for local offline testing while preserving identical API contracts and verification flows.
- **LLM Engine:** Provider fallback chain (Gemini API ➔ OpenAI ➔ Structured Mock Engine).
- **RAG & Search:** Vector search falls back gracefully to relational SQL full-text search if pgvector extension is unindexed.
