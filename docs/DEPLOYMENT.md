# PayPath — Deployment & DevOps Specification

## 1. Target Infrastructure Blueprint
- **Frontend Hosting:** Vercel or Render Static Site (Vite Single Page App).
- **Backend Service:** Render Web Service (FastAPI / Uvicorn).
- **Database:** Render Managed PostgreSQL 16 with `pgvector` extension.
- **Cache / Queue:** Render Managed Redis or local in-memory fallback.
- **Payment Sandbox:** PayPal Developer Sandbox environment.

---

## 2. Render Blueprint (`render.yaml`)
```yaml
services:
  # Backend API
  - type: web
    name: paypath-api
    runtime: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: APP_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: paypath-db
          property: connectionString
      - key: PAYPAL_BASE_URL
        value: https://api-m.sandbox.paypal.com
      - key: PAYPAL_CLIENT_ID
        sync: false
      - key: PAYPAL_CLIENT_SECRET
        sync: false

  # Frontend Web Client
  - type: web
    name: paypath-web
    runtime: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: "./frontend/dist"
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_BASE_URL
        fromService:
          type: web
          name: paypath-api
          property: host

databases:
  - name: paypath-db
    databaseName: paypath
    user: paypath_user
    plan: free
```

---

## 3. Database Backup & Restore Procedures
- **Automated Snapshots:** Enabled via Render Managed Database daily backups.
- **Manual Export Command:**
  ```bash
  pg_dump -h <host> -U <user> -d paypath -Fc -f paypath_backup.dump
  ```
- **Restore Command:**
  ```bash
  pg_restore -h <host> -U <user> -d paypath -c paypath_backup.dump
  ```

