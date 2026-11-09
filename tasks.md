# PayPath — Implementation Task Tracker

## Legend
- **Priority:** `P0` (Blocking / Core MVP), `P1` (High / Hero Flow), `P2` (Important), `P3` (Stretch / Sponsor)
- **Status:** `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `DEFERRED`

---

## Phase 0: Project Memory & Specifications (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T0.1 | Create Root Memory Documents (Brain, memory, architecture, rules, tasks) | P0 | None | DONE | Root documents established and aligned with specification. |
| T0.2 | Create Documentation Suite (`docs/*.md`) | P0 | T0.1 | DONE | All 14 design and specification documents created under `docs/`. |

---

## Phase 1: Foundation & Project Scaffolding (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T1.1 | Initialize FastAPI Backend Architecture | P0 | T0.2 | DONE | Directory structure, settings, logging, async app lifecycle working. |
| T1.2 | Database Engine & SQLAlchemy Models | P0 | T1.1 | DONE | Core models (User, Transaction, Policy, Action, Audit, etc.) defined with async support. |
| T1.3 | Security & Authentication Layer | P0 | T1.2 | DONE | JWT/session auth, password hashing (Argon2/bcrypt), RBAC dependency guards. |
| T1.4 | Initialize React + Vite + Tailwind Frontend | P0 | T1.1 | DONE | Clean modern UI shell with navigation, state store, and theme setup. |

---

## Phase 2: PayCore Subsystem (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T2.1 | PayPal Sandbox OAuth2 Client & Config | P0 | T1.1 | DONE | Token caching, credentials validation, robust error handling. |
| T2.2 | Order Creation & Capture Engine | P0 | T2.1 | DONE | Create order, capture order, store normalized transaction with timeline events. |
| T2.3 | PayPal Refund Engine & Idempotency Vault | P0 | T2.2 | DONE | Execute refund with deduplication and idempotency key checks. |
| T2.4 | Independent Read-Back Verification Agent | P0 | T2.3 | DONE | Query PayPal resource after action and verify amounts, state, currency. |
| T2.5 | Webhook Ingestion & Signature Verification | P1 | T2.2 | DONE | Handle PayPal webhooks idempotently and update transaction status. |

---

## Phase 3: Transaction Intelligence & AG Grid Explorer (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T3.1 | Transaction Normalization & Event Timeline | P0 | T2.2 | DONE | Full lifecycle representation with human-readable status & metadata. |
| T3.2 | AG Grid Transaction Explorer Implementation | P0 | T3.1, T1.4 | DONE | Interactive grid with sorting, filtering, quick search, risk badges, AI summaries. |
| T3.3 | Transaction Detail View & Timeline | P0 | T3.2 | DONE | Deep dive drawer/modal showing timeline, evidence, policy links, audit trail. |

---

## Phase 4: Intent & AI Command Center (P1)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T4.1 | LLM Provider Abstraction & Pydantic Schemas | P1 | T1.1 | DONE | Flexible provider with structured outputs and schemas. |
| T4.2 | Intent Agent (NL to Structured Intent) | P1 | T4.1 | DONE | Extracts budget, category, constraints, and autonomy limits into DB. |
| T4.3 | Interactive AI Command Center Component | P1 | T4.2, T1.4 | DONE | Conversational interface for transaction inquiries and guided actions. |

---

## Phase 5: RAG & Merchant Policy Engine (P1)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T5.1 | Policy Document Ingestion & Chunking | P1 | T1.2 | DONE | Chunking with metadata (merchant, section, return window, damage rules). |
| T5.2 | Vector Storage & Policy Retrieval Engine | P1 | T5.1 | DONE | Vector embeddings (pgvector / similarity search) with tenant filtering. |
| T5.3 | Citation & Evidence Grounding Generator | P1 | T5.2 | DONE | Transparent clause citations attached to policy evaluations. |

---

## Phase 6: Agent Orchestrator & Message Bus (P1)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T6.1 | Typed Inter-Agent Message Protocol | P1 | T4.1 | DONE | Strongly typed messages (`IntentRequest`, `PolicyCheck`, `RefundProposal`, etc.). |
| T6.2 | Multi-Agent Coordinator | P1 | T6.1 | DONE | Orchestrates Intent, Shopping, Policy, Evidence, Risk, Resolution, and Verification agents. |
| T6.3 | Agent Execution Trace Visualizer | P1 | T6.2, T1.4 | DONE | Real-time step-by-step agent trace cards displayed in UI. |

---

## Phase 7: Deterministic Policy Engine & Payment Guard (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T7.1 | Deterministic Rule Evaluator | P0 | T1.2 | DONE | Evaluates spending thresholds, return windows, damage coverage (`ALLOW`, `REVIEW`, `BLOCK`, `ESCALATE`). |
| T7.2 | Payment Guard Pre-Transaction Interceptor | P0 | T7.1 | DONE | Intercepts purchase proposal and verifies budget, merchant safety, policy. |
| T7.3 | Human-in-the-Loop Approval Gateway | P0 | T7.1 | DONE | Gateways requiring user or dual approval before financial execution. |

---

## Phase 8: RECLAIM Post-Purchase Resolution System (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T8.1 | Issue Reporting & Multimodal Evidence Ingestion | P0 | T1.2 | DONE | Secure file upload, Evidence Agent classification of damaged/incorrect items. |
| T8.2 | End-to-End RECLAIM Workflow Engine | P0 | T8.1, T5.3, T7.1, T2.3 | DONE | Issue ➔ Evidence ➔ Policy RAG ➔ AI Proposal ➔ Human Approval ➔ PayPal Refund ➔ Verification. |
| T8.3 | Interactive Resolution Center UI | P0 | T8.2, T1.4 | DONE | Complete interactive refund negotiation & approval control panel. |

---

## Phase 9: Payment Recovery Intelligence (P2)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T9.1 | Duplicate Payment Detector | P2 | T3.1 | DONE | Detects identical amounts/merchants within tight intervals. |
| T9.2 | Recurring Payment & Subscription Detector | P2 | T3.1 | DONE | Identifies subscriptions, renewal intervals, unexpected spikes. |

---

## Phase 10: Shopping Agent & Agentic Commerce (P1)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T10.1 | Product Catalog Integration (Channel3 / Demo) | P1 | T4.2 | DONE | Product search, filtering by budget/intent, comparison. |
| T10.2 | Agentic Purchase Proposal & Checkout Flow | P1 | T10.1, T7.2, T2.2 | DONE | Propose product ➔ Guard authorization ➔ User approval ➔ PayPal sandbox checkout. |

---

## Phase 11: Multi-Merchant & Notification Systems (P2)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T11.1 | Merchant Portal & Policy Management | P2 | T5.1 | DONE | Multi-tenant merchant profile, policy upload & publishing. |
| T11.2 | Notification Center & Delivery Adapters | P2 | T1.2 | DONE | In-app alerts, email notification adapter with template support. |

---

## Phase 12: Sponsor Integrations & Documentation (P1)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T12.1 | AG Grid Advanced Integration | P1 | T3.2 | DONE | Rich cell renderers, quick filter, status aggregation. |
| T12.2 | Postman Collection & Automated API Tests | P1 | T1.1 | DONE | Full API collection exported to `docs/postman/` with tests. |
| T12.3 | Render Deployment Blueprint (`render.yaml`) | P1 | T1.1 | DONE | Infrastructure-as-code deployment configuration for backend, frontend, postgres, redis. |
| T12.4 | Elastic Observability & Hybrid Search Adapter | P2 | T1.1 | DONE | Structured audit event stream logging adapter. |

---

## Phase 13+: Runtime Stabilization, PostgreSQL Migration & Hardening (P0)
| ID | Task | Priority | Dependencies | Status | Acceptance Criteria |
|---|---|---|---|---|---|
| T13.1 | Diagnose & Resolve Localhost Link Failure | P0 | None | DONE | Port inspection, background Uvicorn (:8000) & Vite (:5173) launched and verified. |
| T13.2 | PostgreSQL 16 Authoritative Database Migration | P0 | T13.1 | DONE | Service verified, `paypath` DB created, silent SQLite fallback removed, 14 tables verified. |
| T13.3 | Asynchronous Alembic Database Migrations | P0 | T13.2 | DONE | Alembic initialized, autogenerated `initial_schema` revision stamped to head. |
| T13.4 | Authentication & MFA (TOTP) Security Hardening | P0 | T13.2 | DONE | TOTP setup & verification endpoints, password reset token hashing & expiry, token revocation. |
| T13.5 | File Upload Security & Magic Byte Inspection | P0 | T13.2 | DONE | 10MB ceiling, JPEG/PNG/WEBP/PDF magic byte validation, path traversal neutralization. |
| T13.6 | Frontend UX Optimization & Intent Prefetching | P1 | T13.1 | DONE | AG Grid row hover prefetching, Persona switcher, typography tokens, zero build errors. |
| T13.7 | Documentation Suite Expansion | P1 | None | DONE | All 17 newly required documents created and cross-linked under `docs/`. |
| T13.8 | Comprehensive Pytest Suite Expansion | P0 | T13.4, T13.5 | DONE | 23 passed unit & integration tests covering all critical flows. |
