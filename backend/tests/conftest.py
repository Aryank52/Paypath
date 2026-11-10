import os
import pytest
import asyncio
from pathlib import Path

TEST_DB_FILE = Path(__file__).parent.parent / "test_paypath.db"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_FILE.as_posix()}"

from app.core.database import init_db, engine, Base, AsyncSessionLocal
from app.core.config import settings
import app.models  # Ensure all SQLAlchemy models are registered in Base.metadata
from app.services.seed_service import seed_demo_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    settings.APP_ENV = "test"
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE.as_posix()}"
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass

    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)
        await engine.dispose()

    asyncio.run(_init())

    yield

    # Cleanup test db after test suite
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass
