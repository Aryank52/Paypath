import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.observability import logger
from app.services.seed_service import seed_demo_data

from app.api.routes import (
    auth_router,
    transactions_router,
    paycore_router,
    intent_router,
    shop_router,
    guard_router,
    reclaim_router,
    recover_router,
    policies_router,
    agents_router,
    audit_router,
    merchants_router,
    webhooks_router,
    notifications_router,
    system_router,
    ml_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # In test mode, table creation and seeding are managed by conftest fixtures to prevent concurrent race conditions
    if settings.APP_ENV != "test":
        logger.info("Initializing PayPath database tables...")
        await init_db()
        
        # Ensure storage upload directory exists
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
        os.makedirs(upload_dir, exist_ok=True)

        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)
            # Hydrate RAG vector store from authoritative PostgreSQL 16 policy_chunks
            from app.rag.vector_store import vector_store
            await vector_store.load_from_db(session)
            logger.info(f"Loaded {len(vector_store.chunks)} policy chunks from PostgreSQL into vector store.")
        
        logger.info("PayPath backend startup sequence completed successfully.")
        yield
        logger.info("PayPath backend shutting down...")
    else:
        # In test mode, ensure upload dir and vector store are ready without competing with fixtures
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
        os.makedirs(upload_dir, exist_ok=True)
        try:
            from app.rag.vector_store import vector_store
            async with AsyncSessionLocal() as session:
                await vector_store.load_from_db(session)
        except Exception:
            pass
        yield

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Transaction Intelligence, Agentic Commerce & Payment Action Platform",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

from fastapi.responses import RedirectResponse

@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.get("/", include_in_schema=False)
async def root_index():
    return {
        "service": settings.APP_NAME,
        "status": "ONLINE",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/system/health",
        "version": "1.0.0"
    }

# CORS configuration locked down to trusted development and production origins
BASE_ALLOWED_ORIGINS = [
    "https://paypath.finance",
    "https://www.paypath.finance",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

ALLOWED_ORIGINS = list(BASE_ALLOWED_ORIGINS)
if getattr(settings, "ALLOWED_ORIGINS", None):
    extra_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    ALLOWED_ORIGINS.extend(extra_origins)

# Ensure no wildcard origins are ever present
ALLOWED_ORIGINS = [o for o in set(ALLOWED_ORIGINS) if o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Production-grade Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    connect_sources = (
        "'self' https://api-m.sandbox.paypal.com https://api-m.paypal.com https://generativelanguage.googleapis.com"
    )
    if settings.APP_ENV != "production":
        connect_sources += " http://localhost:* http://127.0.0.1:*"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.paypal.com https://*.paypalobjects.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https: blob:; "
        f"connect-src {connect_sources}; "
        "frame-src 'self' https://www.sandbox.paypal.com https://www.paypal.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    if settings.APP_ENV == "production" or request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Global Structured Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected system error occurred. Please try again.",
                "path": request.url.path
            }
        }
    )

from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

# Ensure upload directory exists and mount safely
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Health & Readiness checks
@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    db_status = "CONNECTED"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"ERROR: {str(e)}"

    return {
        "status": "HEALTHY" if db_status == "CONNECTED" else "DEGRADED",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "PostgreSQL 16",
        "database_status": db_status,
        "paypal_configured": bool(settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET)
    }

# Register all API routes under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(transactions_router, prefix=settings.API_V1_STR)
app.include_router(paycore_router, prefix=settings.API_V1_STR)
app.include_router(intent_router, prefix=settings.API_V1_STR)
app.include_router(shop_router, prefix=settings.API_V1_STR)
app.include_router(guard_router, prefix=settings.API_V1_STR)
app.include_router(reclaim_router, prefix=settings.API_V1_STR)
app.include_router(recover_router, prefix=settings.API_V1_STR)
app.include_router(policies_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(merchants_router, prefix=settings.API_V1_STR)
app.include_router(webhooks_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

