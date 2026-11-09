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
    notifications_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PayPath database tables...")
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)
    logger.info("PayPath backend startup sequence completed successfully.")
    yield
    logger.info("PayPath backend shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Transaction Intelligence, Agentic Commerce & Payment Action Platform",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS middleware for React / Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Health & Readiness checks
@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

