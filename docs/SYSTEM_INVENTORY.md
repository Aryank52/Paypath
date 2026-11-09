# PayPath — Full System Inventory & Component Registry

**Document Version:** 1.0 (Phase 15 Production Architecture)  
**System Name:** PayPath  
**Architecture Classification:** Autonomous Transaction Intelligence & Agentic Commerce Platform  
**System Authoritative Database:** PostgreSQL 16.15  

---

## 1. System Inventory Matrix

| Subsystem | Status | Implementation Class | Runtime Dependency | Configuration Keys | Automated Tests | Known Issues / Gaps |
|---|---|---|---|---|---|---|
| **Frontend** | `OPERATIONAL` | React 19, TypeScript, Vite, Tailwind v4, AG Grid, TanStack Query v5, Lucide Icons | Node.js v24, npm 11 | `vite.config.ts`, `VITE_API_BASE_URL` | `npm run build` (tsc + vite) | None; bundle builds cleanly in 33s. |
| **Backend** | `OPERATIONAL` | FastAPI, Python 3.12, Pydantic v2, Async SQLAlchemy 2.0 | Python 3.12, Uvicorn | `HOST=127.0.0.1`, `PORT=8000`, `PYTHONPATH` | `test_api_endpoints.py`, `test_main.py` | None; ASGI lifespan fully initialized. |
| **Database** | `OPERATIONAL` | PostgreSQL 16.15 with AsyncPG connection pool | `postgresql-x64-16` Windows service | `DATABASE_URL=postgresql+asyncpg://...` | Schema foreign key checks, `pg_dump` smoke test | Must enforce unified schema across all expanded tables. |
| **Redis** | `ACTIVE_FALLBACK` | In-memory token revocation & rate limit store with Redis URL adapter | Optional external Redis service | `REDIS_URL` | `test_auth_session_revocation` | Local fallback used when Redis URL is not set. |
| **PayPal** | `ACTIVE_FALLBACK` | PayCore Client v2 (`/v2/checkout/orders`, `/v2/payments/captures`, `/refund`) | PayPal Sandbox REST API | `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_BASE_URL` | `test_paycore_reclaim.py`, `test_financial_invariants` | Sandbox API requires developer credentials in `.env`; deterministic sandbox mock active in absence. |
| **LLM Engine** | `ACTIVE_FALLBACK` | Multi-provider abstraction (`GoogleGenAIProvider`, fallback deterministic mock) | Google Gemini API (gemini-2.5-flash) | `GEMINI_API_KEY`, `LLM_PROVIDER="gemini"` | `test_agents.py` | Mock returns deterministic schema-valid JSON when API key is unset. |
| **RAG Engine** | `OPERATIONAL` | Policy chunking, PostgreSQL persistence (`policy_chunks`), vector cosine similarity | PostgreSQL `policy_chunks` table, numpy embeddings | `EMBEDDING_MODEL` | `test_policy_engine.py`, API tests | In-memory vector store needs pgvector extension binding for >10k chunks. |
| **Agents** | `OPERATIONAL` | Multi-agent state machine (Intent, Shopping, Policy, Evidence, Risk, Resolution, Verification) | Python async orchestrator | Internal agent contracts | `test_agents.py` (4/4 passing) | Agent run metadata must be persisted to PostgreSQL `agent_runs`. |
| **ML Engine** | `INTEGRATION_TARGET`| Feature pipeline, XGBoost (Risk), Isolation Forest (Anomaly) | `scikit-learn`, `xgboost`, `numpy`, `pandas` | `ML_MODEL_DIR`, `ML_FEATURE_VERSION` | Target: `test_ml_pipeline.py` | Currently using heuristic risk scoring; supervised & unsupervised models to be trained on synthetic transaction baseline. |
| **Notifications**| `OPERATIONAL` | In-app notification queue persisted in `notifications` table | PostgreSQL | Internal event emitter | `test_api_endpoints.py` | Outbound push/SMS requires external provider. |
| **Email** | `FEATURE_FLAGGED`| Resend / SendGrid webhook client | External SMTP/HTTP API | `ENABLE_EMAIL=False`, `RESEND_API_KEY` | None | Safely disabled via feature flag; in-app notifications active. |
| **File Uploads** | `OPERATIONAL` | Binary magic-byte inspector (`\xFF\xD8\xFF`, `\x89PNG`, `%PDF`) | Local secure storage | `UPLOAD_DIR=backend/uploads/evidence` | `test_magic_byte_validation_rejection` | Storage abstraction (`StorageProvider`) needed for cloud deployment. |
| **Merchant Sys** | `OPERATIONAL` | Multi-merchant tenant isolation, policy upload, RBAC admin endpoints | PostgreSQL `merchants`, `merchant_policies` | Internal tenant routing | `test_rbac_merchant_operations_denial` | 1 merchant seeded currently; requires expanding to 5 diverse merchants. |
| **Voice** | `OPERATIONAL` | Web Speech API frontend voice synthesizer and microphone listener | Browser Web Speech API | `ENABLE_VOICE=True` | Frontend component checks | Requires Chrome/Edge browser speech engine permissions. |
| **Observability** | `OPERATIONAL` | Python structured JSON logging with ISO-8601 timestamps, audit log table | PostgreSQL `audit_logs` | `LOG_LEVEL=INFO` | `test_complete_paycore_and_reclaim_lifecycle` | Append-only audit table captures all financial mutations. |
| **Deployment** | `OPERATIONAL` | Windows localhost native, Alembic migrations, Docker / Render manifests | OS / Container | `alembic.ini`, `render.yaml` | Alembic zero-to-head migration test | Local development fully automated. |

---

## 2. Machine-Readable Metadata (JSON)

```json
{
  "system": "PayPath",
  "version": "1.0.0-rc1",
  "authoritative_store": "PostgreSQL 16.15",
  "components": {
    "frontend": {"framework": "React 19", "port": 5173, "status": "UP"},
    "backend": {"framework": "FastAPI", "port": 8000, "status": "UP"},
    "database": {"engine": "PostgreSQL", "port": 5432, "schema_version": "0199be8d9868", "status": "CONNECTED"},
    "paypal": {"engine": "PayCore", "mode": "SANDBOX_DUAL_MODE"},
    "security": {"mfa": "TOTP_RFC6238", "rbac": "ENFORCED", "idor_defense": "ENFORCED"}
  }
}
```

