import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["service"] == "PayPath"

@pytest.mark.asyncio
async def test_transactions_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        first_tx = data[0]
        assert "amount" in first_tx
        assert "status" in first_tx

@pytest.mark.asyncio
async def test_intent_parsing_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"prompt": "Find me wireless noise-cancelling headphones under $100 for travel"}
        response = await client.post("/api/v1/intent/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "headphones"
        assert data["purpose"] == "travel"
        assert data["budget"] == 100.0

@pytest.mark.asyncio
async def test_guard_evaluation_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "amount": 89.0,
            "merchant_name": "Nova Electronics",
            "category": "headphones"
        }
        response = await client.post("/api/v1/guard/evaluate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "ALLOW"
        assert data["is_allowed"] is True

@pytest.mark.asyncio
async def test_agent_commerce_workflow_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"prompt": "I need headphones under $100 for travel."}
        response = await client.post("/api/v1/agents/run-commerce", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "selected_product" in data
        assert "trace" in data
        assert len(data["trace"]) >= 2
