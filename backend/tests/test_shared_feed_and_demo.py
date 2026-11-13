import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_shared_feed_unauthenticated_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/transactions/feed")
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_shared_feed_authenticated_returns_sanitized_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create demo session as shopper
        session_res = await client.post("/api/v1/demo/session", json={"persona": "shopper"})
        assert session_res.status_code == 200
        token = session_res.json()["access_token"]

        # Call feed with token
        feed_res = await client.get(
            "/api/v1/transactions/feed",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert feed_res.status_code == 200
        data = feed_res.json()
        assert "total_records" in data
        assert "items" in data
        assert data["provenance"] == "RENDER_POSTGRESQL_16"
        assert len(data["items"]) > 0

        # Inspect first item for sanitization
        item = data["items"][0]
        assert "public_reference" in item
        assert item["public_reference"].startswith("PP-TRX-")
        assert "merchant_name" in item
        assert "item" in item
        assert "amount" in item
        assert "currency" in item
        assert "payment_state" in item
        assert "risk_level" in item
        assert "verification_status" in item
        assert "source" in item

        # Verify sensitive fields are strictly NOT present
        sensitive_keys = [
            "user_id", "merchant_id", "id", "paypal_order_id",
            "paypal_capture_id", "meta_info", "events", "email"
        ]
        for key in sensitive_keys:
            assert key not in item, f"Sensitive key '{key}' leaked in shared feed item!"

@pytest.mark.asyncio
async def test_demo_session_creation_and_switching():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create demo session as shopper
        shopper_res = await client.post("/api/v1/demo/session", json={"persona": "shopper"})
        assert shopper_res.status_code == 200
        shopper_data = shopper_res.json()
        assert shopper_data["active_persona"] == "SHOPPER"
        assert shopper_data["role"] == "USER"
        assert shopper_data["is_demo"] is True
        token = shopper_data["access_token"]

        # 2. Switch to merchant
        merchant_res = await client.post(
            "/api/v1/demo/switch",
            json={"persona": "merchant"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert merchant_res.status_code == 200
        merchant_data = merchant_res.json()
        assert merchant_data["active_persona"] == "MERCHANT_ADMIN"
        assert merchant_data["role"] == "MERCHANT_ADMIN"
        merchant_token = merchant_data["access_token"]

        # 3. Switch to platform admin
        admin_res = await client.post(
            "/api/v1/demo/switch",
            json={"persona": "platform_admin"},
            headers={"Authorization": f"Bearer {merchant_token}"}
        )
        assert admin_res.status_code == 200
        admin_data = admin_res.json()
        assert admin_data["active_persona"] == "PLATFORM_ADMIN"
        assert admin_data["role"] == "PLATFORM_ADMIN"

        # 4. Exit demo
        exit_res = await client.post(
            "/api/v1/demo/exit",
            headers={"Authorization": f"Bearer {admin_data['access_token']}"}
        )
        assert exit_res.status_code == 200

@pytest.mark.asyncio
async def test_persona_switching_privilege_escalation_defense():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register a normal non-demo user
        email = "test_normal_shopper@example.com"
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "SecurePassword123!",
            "full_name": "Normal Shopper"
        })
        assert reg_res.status_code == 200

        # Login as normal user
        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # Attempt to escalate to platform_admin
        escalate_res = await client.post(
            "/api/v1/auth/persona/switch",
            json={"persona": "platform_admin"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert escalate_res.status_code == 403
        assert "Access denied" in escalate_res.json()["detail"]

        # Attempt to escalate to merchant
        escalate_merchant = await client.post(
            "/api/v1/auth/persona/switch",
            json={"persona": "merchant"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert escalate_merchant.status_code == 403
        assert "Access denied" in escalate_merchant.json()["detail"]

@pytest.mark.asyncio
async def test_demo_mode_blocks_credential_modification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Start demo session
        session_res = await client.post("/api/v1/demo/session", json={"persona": "shopper"})
        assert session_res.status_code == 200
        token = session_res.json()["access_token"]

        # Attempt password change in demo mode
        pw_res = await client.post(
            "/api/v1/auth/password/change",
            json={"current_password": "any", "new_password": "new_secret_pass"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert pw_res.status_code == 403
        assert "disabled in Demo Mode" in pw_res.json()["detail"]

