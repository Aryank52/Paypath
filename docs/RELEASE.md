# PayPath Production Release Notes — Version 1.0.0

## Release Summary
**PayPath 1.0.0** is the release-ready version for the PayPal & AI Agentic Commerce Hackathon. It brings end-to-end integration between PayPal Sandbox, multi-agent AI deliberation (Google Gemini + deterministic policy engine), and PostgreSQL 16 authoritative transaction ledger.

## What's Included in 1.0.0

### Core Platform
- **FastAPI ASGI Backend**: High-performance asynchronous API service.
- **Authoritative PostgreSQL 16**: Fully normalized database with Alembic migration versioning.
- **PayCore PayPal Engine**: Independent verification against PayPal Sandbox (`Orders v2`, `Payments v2`).
- **Deterministic Policy Engine**: Four-state policy validation (`ALLOW`, `REVIEW`, `BLOCK`, `ESCALATE`).
- **Tenant-Isolated RAG**: Vector similarity search over merchant policies with strict `merchant_id` partitioning.
- **RECLAIM Resolution System**: End-to-end damaged goods claim with photo evidence OCR, policy citation, and human approval.

### Frontend
- **React 19 + Vite + Tailwind CSS**: Zero-compile-error production build.
- **AG Grid Financial Explorer**: Interactive transaction lifecycle with quick search, column filtering, and prefetching on hover.
- **AI Command Center**: Real-time modal with Web Speech API voice synthesis and speech-to-intent.
- **Persona Switcher**: Switch seamlessly between Shopper mode and Merchant Admin mode.
- **Payment Guard Studio & Recovery Intelligence**: Anomaly detection and subscription tracker.

### Security Hardening
- TOTP MFA two-factor authentication.
- Cryptographically secure password reset token hashing.
- File upload magic-byte verification and path traversal neutralization.
- In-memory JWT revocation blacklist.

### Verification Status
- Backend Pytest Suite: **23 passed**.
- Frontend Build: **0 TypeScript errors, 2.96s build**.
- Localhost Health: **FastAPI (:8000) and Vite (:5173) active and communicating**.

