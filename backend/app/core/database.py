from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

import logging

logger = logging.getLogger("paypath.database")

from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

# Configure SQLite or PostgreSQL async connection args
connect_args = {}
engine_kwargs = {
    "echo": False,
    "future": True,
}

# Ensure asyncpg dialect is enforced for PostgreSQL
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if "sqlite" in db_url:
    if settings.APP_ENV not in ("test", "testing"):
        logger.warning(
            "WARNING: Running on SQLite in '%s' mode. "
            "PostgreSQL is the authoritative production database for PayPath.",
            settings.APP_ENV
        )
    connect_args = {"check_same_thread": False}
    if settings.APP_ENV in ("test", "testing"):
        engine_kwargs["poolclass"] = NullPool
else:
    if settings.APP_ENV in ("test", "testing"):
        engine_kwargs["poolclass"] = NullPool
    else:
        # PostgreSQL connection pool configuration
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        })

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

