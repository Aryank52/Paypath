# PayPath Production Deployment Runbook

**Document Version:** 1.0.0  
**Target Environments:** Render (FastAPI + PostgreSQL 16), Vercel (React + Vite), PayPal Developer Sandbox, Supabase Storage  

---

## 1. Prerequisites and Infrastructure Provisioning

### 1.1 Render Infrastructure
1. **PostgreSQL Database:**
   - Managed PostgreSQL 16.15 instance.
   - Internal Database URL: `postgresql://paypath_db_user:PASSWORD@dpg-...-a/paypath_db`
   - Connection Pooling: Disabled in URI (SQLAlchemy asyncpg manages application-level connection pool).
2. **Web Service:**
   - Environment: Python 3.12
   - Region: Oregon (US West) or Frankfurt (EU Central)
   - Branch: `main`
   - Build Command: `pip install --upgrade pip && pip install -r backend/requirements.txt`
   - Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

### 1.2 Vercel Infrastructure
1. **Frontend Project:**
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Node Version: 20.x

---

## 2. Environment Variables & Secret Configuration

### 2.1 Render Web Service Environment Variables

| Variable Name | Required | Example / Production Value | Purpose |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | Yes | `production` | Enables strict fail-closed security and disables dev fallbacks |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host/db` | Authoritative PostgreSQL 16 connection string |
| `SECRET_KEY` | Yes | *Cryptographically random 64-char hex string* | JWT signing and HMAC validation |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` (24 hours) | JWT expiration lifetime |
| `ALLOWED_ORIGINS` | Yes | `https://paypath.finance,https://paypath-frontend.vercel.app` | CORS origins permitted to access backend |
| `PAYPAL_MODE` | Yes | `sandbox` | PayPal environment mode |
| `PAYPAL_CLIENT_ID` | Yes | *PayPal Sandbox Client ID* | PayPal REST API client |
| `PAYPAL_CLIENT_SECRET` | Yes | *PayPal Sandbox Client Secret* | PayPal REST API client secret |
| `PAYPAL_BASE_URL` | Yes | `https://api-m.sandbox.paypal.com` | Base endpoint for PayPal API calls |
| `PAYPAL_WEBHOOK_ID` | Yes | *Registered Webhook ID* | Registered webhook ID for signature verification |
| `SUPABASE_URL` | Yes | `https://xyzproject.supabase.co` | Supabase API endpoint for evidence storage |
| `SUPABASE_KEY` | Yes | *Supabase Service Role Key* | Private bucket read/write authorization |
| `SUPABASE_STORAGE_BUCKET`| No | `paypath-evidence` | Private evidence bucket name |
| `GEMINI_API_KEY` | Yes | *Google AI Studio API Key* | Intent analysis & non-authoritative intelligence |

### 2.2 Vercel Frontend Environment Variables

| Variable Name | Required | Example / Production Value | Purpose |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | `https://paypath-8u9a.onrender.com` | Root origin of Render backend API |

---

## 3. Step-by-Step Deployment Execution

### Step 1: Git Push to Trigger CI/CD
```bash
git add .
git commit -m "chore(release): certified production release"
git push origin main
```
- GitHub Actions verifies hygiene, passes 53 backend tests, and builds frontend.
- Render and Vercel webhooks detect the push to `main`.

### Step 2: Render Zero-Downtime Deployment
- Render installs dependencies from `backend/requirements.txt`.
- Uvicorn boots `app.main:app`.
- FastAPI lifespan connects to PostgreSQL 16, runs Alembic migrations, and triggers `seed_demo_data`.
- Render probes `/health`. When HTTP 200 is received, traffic cuts over to the new container.

### Step 3: Vercel Static Edge Deployment
- Vercel runs `npm run build` inside `frontend/`.
- Compiles TypeScript and packages assets into `frontend/dist/`.
- Deploys static assets across global edge nodes with instant atomic switch.

---

## 4. Rollback & Emergency Procedures

1. **Backend Rollback:**
   - In Render Dashboard: Web Service -> Deploys -> Select previous successful deploy -> Click "Rollback".
2. **Frontend Rollback:**
   - In Vercel Dashboard: Project -> Deployments -> Select previous build -> Click "Instant Rollback".
3. **Database Restore:**
   - In Render PostgreSQL: Backups tab -> Choose desired snapshot -> Click "Restore to New Instance" or restore point-in-time.

