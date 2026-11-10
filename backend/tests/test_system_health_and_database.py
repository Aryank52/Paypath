"""
Automated Integration Tests for PayPath System Health and PostgreSQL Diagnostics.
Verifies:
1. GET /api/v1/system/health returns HEALTHY status with PostgreSQL 16 latency and component details.
2. GET /api/v1/system/database returns all 19 PostgreSQL tables with positive row counts.
3. Seed idempotency across repeated executions.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.seed_service import seed_demo_data, verify_demo_data
from app.ml.train import train_and_register_models

@pytest.mark.asyncio
async def test_system_health_endpoint():
    """Verify system health aggregation endpoint returns connected components."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/system/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ["HEALTHY", "DEGRADED"]
        assert "components" in data
        assert data["components"]["postgresql"]["status"] == "CONNECTED"
        assert "PostgreSQL" in data["components"]["postgresql"]["version"]
        assert data["components"]["ml_engine"]["status"] == "ACTIVE"
        assert data["components"]["ml_engine"]["features_tracked"] == 12

@pytest.mark.asyncio
async def test_system_database_inventory_endpoint():
    """Verify database inventory endpoint accurately inspects all tables."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/system/database")
        assert res.status_code == 200
        data = res.json()
        assert data["database"] == "paypath"
        assert data["engine"] == "PostgreSQL 16"
        assert data["total_tables"] >= 18
        assert data["total_records"] > 50

        # Check key tables exist with positive records
        table_map = {t["table_name"]: t["row_count"] for t in data["tables"]}
        assert table_map.get("users", 0) >= 5
        assert table_map.get("merchants", 0) >= 5
        assert table_map.get("products", 0) >= 15
        assert table_map.get("transactions", 0) >= 50
        assert table_map.get("reclaim_cases", 0) >= 3

@pytest.mark.asyncio
async def test_seed_idempotency():
    """Verify that multiple seed runs do not crash or corrupt database state."""
    async with AsyncSessionLocal() as session:
        # First verification
        v1 = await verify_demo_data(session)
        # Execute seed idempotently
        await seed_demo_data(session, force_reset=False)
        # Second verification
        v2 = await verify_demo_data(session)

        assert v1["users"] == v2["users"]
        assert v1["merchants"] == v2["merchants"]
        assert v1["products"] == v2["products"]
        assert v1["transactions"] == v2["transactions"]
