# PayPath — Implementation Plan & Phase Milestones

## 1. Roadmap Overview
The implementation is structured into 16 tightly coupled phases, prioritizing the PayPal Core vertical slice and security controls before advanced multi-agent capabilities.

```text
Phase 0: Project Memory & Specifications (DONE)
Phase 1: Foundation (FastAPI + React + DB Engine) (CURRENT)
Phase 2: PayCore Subsystem (PayPal Sandbox OAuth2, Order, Capture, Refund, Verification)
Phase 3: Transaction Intelligence & AG Grid Explorer
Phase 4: Intent & AI Command Center
Phase 5: RAG & Merchant Policy Engine
Phase 6: Agent Orchestrator & Message Bus
Phase 7: Deterministic Policy Engine & Payment Guard
Phase 8: RECLAIM Post-Purchase Resolution System
Phase 9: Payment Recovery Intelligence (Duplicates & Subscriptions)
Phase 10: Shopping Agent & Agentic Commerce
Phase 11: Multi-Merchant & Notification Systems
Phase 12: Sponsor Integrations (AG Grid, Render, Postman, Elastic)
Phase 13: Voice & Multimodal Enhancements
Phase 14: End-to-End Testing & Security Audit
Phase 15: Demo Seed Data & Narrative Polish
Phase 16: Deployment & Submission Package
```

## 2. Phase-by-Phase Deliverables

### Phase 1: Foundation Setup
- Backend structure: `backend/app/{core, api, models, schemas, paycore, agents, policies, services}`
- Database connection pool with async SQLAlchemy, model declarations, auto-creation fallback.
- React frontend: Vite + Tailwind CSS + Lucide icons + React Query + Zustand layout shell.

### Phase 2: PayCore & PayPal Sandbox Engine
- `app/paycore/paypal_client.py`: Async HTTPX client for PayPal v2 REST APIs with client credential token rotation.
- Order creation & capture service.
- Idempotent refund execution service.
- Independent read-back verifier (`GET /v2/payments/captures/{id}` and `GET /v2/payments/refunds/{id}`).

### Phase 3: Transaction Intelligence & AG Grid
- Normalization pipeline converting PayPal webhook/API payloads into unified `Transaction` and `TransactionEvent` entities.
- AG Grid React component with custom cell renderers, risk status badges, and expandable lifecycle drawer.

### Phase 4-8: AI, RAG, Agents & RECLAIM
- Structured JSON LLM adapter (Gemini API & Fallback Engine).
- Merchant policy chunking, pgvector search, and clause citation.
- Agent Orchestrator coordinating Intent, Shopping, Policy, Evidence, Risk, and Resolution agents.
- Complete RECLAIM dispute center: Photo evidence ➔ Policy RAG ➔ AI proposal ➔ Human approval ➔ PayPal refund ➔ Independent verification.

### Phase 9-16: Commerce, Recovery & Polish
- Duplicate charge & subscription recurring payment detectors.
- Channel3 / normalized product catalog shopping interface with Payment Guard spend limits.
- Render deployment blueprint (`render.yaml`) and Postman API collection.

