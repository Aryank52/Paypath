# PayPath — Sponsor Integration Architecture

## 1. PayPal (Primary Hackathon Integration)
- **Role:** Central payment and refund rail.
- **Implementation:** `app/paycore/` encapsulates PayPal Orders v2, Payments v2, and Webhooks APIs.
- **Key Differentiation:** Dual-phase mutation verification (secondary read-back after order capture and refund to guarantee authoritative settlement).
- **Environment:** Strictly PayPal Sandbox credentials via environment variables (`PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`).

---

## 2. AG Grid (Data Grid Sponsor Opportunity)
- **Role:** Powers the **Transaction Intelligence Explorer**.
- **Implementation:** Custom React data grid rendering transactions with:
  - Complex custom cell renderers (Risk Badges, Status Pills, Verified by PayPal indicators).
  - Quick text search and column filtering.
  - Lifecycle event drawer expansion on row click.
  - Sorting and grouping by merchant, status, and risk level.

---

## 3. Render (Deployment & Cloud Infrastructure Sponsor)
- **Role:** Full-stack production deployment.
- **Implementation:** Infrastructure-as-code `render.yaml` defining:
  - FastAPI backend web service.
  - React frontend static site.
  - Managed PostgreSQL 16 database.
  - Background asynchronous workers for RAG chunking and verification.

---

## 4. Postman (API Testing & Collaboration Sponsor)
- **Role:** API workflow automation and contract verification.
- **Implementation:** Complete Postman collection provided in `docs/postman/paypath.postman_collection.json` covering:
  - Auth, Transactions, PayCore orders, Refund mutations, Independent Verification, and RECLAIM workflows.

---

## 5. Channel3 / Product Catalog
- **Role:** Normalized product feed for the Shopping Agent.
- **Implementation:** `app/services/shopping_service.py` provides an adapter interface with real schema normalization and fallback demo product catalogs.

---

## 6. Elastic (AI & Search Observability)
- **Role:** Structured audit logging and hybrid search telemetry.
- **Implementation:** `app/core/observability.py` provides an Elastic adapter for indexing tamper-resistant audit logs and agent execution metrics.

---

## 7. Bryntum (Visual Workflow Timeline)
- **Role:** Visual Gantt/Timeline representation for complex, multi-party dispute resolutions.
- **Implementation:** Timeline component mapping resolution stages (Issue Logged ➔ Evidence Submitted ➔ AI Evaluated ➔ Approval Granted ➔ Refund Settled).
