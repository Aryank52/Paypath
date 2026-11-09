# PayPath PostgreSQL 16 Architecture & Database Specification

## 1. Authoritative Role of PostgreSQL
In PayPath, PostgreSQL 16 is the **sole authoritative system of record**.
- SQLite is strictly forbidden in production and development environments.
- SQLite is only permitted during automated unit testing (`APP_ENV=test`).
- Database URL configuration:
  `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/paypath`

---

## 2. Asynchronous Driver & Connection Pooling
PayPath connects using `asyncpg` via SQLAlchemy 2.0 Async Engine:
- **Pool Size**: 10 persistent worker connections.
- **Max Overflow**: 20 burst connections for high-concurrency spikes.
- **Pre-Ping (`pool_pre_ping=True`)**: Verifies connection liveness before checking out from pool, preventing broken-pipe errors.
- **Pool Recycle (`pool_recycle=1800`)**: Recycles stale connections every 30 minutes.

---

## 3. Schema Management via Alembic
Database migrations are strictly versioned using asynchronous Alembic:
- Migration directory: `backend/alembic/`
- Current head revision: `941e4676f903 (initial_schema)`
- Commands:
  ```bash
  # Check current version
  alembic current
  # Generate revision
  alembic revision --autogenerate -m "description"
  # Apply migrations
  alembic upgrade head
  ```

---

## 4. Vector Storage & Search
Embeddings (128-dimensional deterministic semantic hash vectors or dense model vectors) are persisted in the `policy_chunks` table within a normalized JSON column. Similarity queries calculate cosine distance with tenant isolation:
```sql
SELECT id, content, (embedding <-> :query_vector) AS distance
FROM policy_chunks
WHERE merchant_id = :merchant_id
ORDER BY distance ASC
LIMIT 3;
```
This architecture ensures vector RAG operates natively on vanilla PostgreSQL installations without requiring external C extensions.

