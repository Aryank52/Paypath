import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import generate_totp_secret, verify_totp_code
import pyotp

@pytest.mark.asyncio
async def test_auth_session_revocation():
    """Verify that calling /logout invalidates the specific JWT jti immediately."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login to obtain access token
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "demo@paypath.finance",
            "password": "paypath123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Authenticated access works
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "demo@paypath.finance"

        # 3. Logout to revoke token
        logout_res = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 200

        # 4. Reusing the revoked token MUST be rejected
        revoked_access_res = await client.get("/api/v1/auth/me", headers=headers)
        # Fallback to demo user without auth may happen in pure dev fallback, but with invalid token it must fail or reject
        assert revoked_access_res.status_code in [401, 403]

@pytest.mark.asyncio
async def test_mfa_adversarial_flow():
    """Complete adversarial testing of TOTP 2FA lifecycle."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register a unique user for this test
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": "mfa_tester@paypath.ai",
            "password": "SecurePassword2026!",
            "full_name": "MFA Test User"
        })
        assert reg_res.status_code == 200

        # Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "mfa_tester@paypath.ai",
            "password": "SecurePassword2026!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Setup MFA
        setup_res = await client.post("/api/v1/auth/mfa/setup", headers=headers)
        assert setup_res.status_code == 200
        data = setup_res.json()
        assert "secret" in data
        assert "otpauth_url" in data
        assert data["otpauth_url"].startswith("otpauth://totp/PayPath:")
        secret = data["secret"]

        # 2. Adversarial: Try to enable with wrong 6-digit code
        bad_enable = await client.post("/api/v1/auth/mfa/enable", json={"code": "000000"}, headers=headers)
        assert bad_enable.status_code == 400

        # 3. Enable with valid TOTP code
        totp = pyotp.TOTP(secret)
        good_enable = await client.post("/api/v1/auth/mfa/enable", json={"code": totp.now()}, headers=headers)
        assert good_enable.status_code == 200
        assert good_enable.json()["mfa_enabled"] is True

        # 4. Login now requires MFA
        login_mfa_req = await client.post("/api/v1/auth/login", json={
            "email": "mfa_tester@paypath.ai",
            "password": "SecurePassword2026!"
        })
        assert login_mfa_req.status_code == 200
        assert login_mfa_req.json()["mfa_required"] is True
        assert login_mfa_req.json()["access_token"] == ""

        # 5. Adversarial: Login with wrong MFA code
        login_fail_mfa = await client.post("/api/v1/auth/login", json={
            "email": "mfa_tester@paypath.ai",
            "password": "SecurePassword2026!",
            "mfa_code": "999999"
        })
        assert login_fail_mfa.status_code == 401

        # 6. Login with correct MFA code succeeds
        login_success_mfa = await client.post("/api/v1/auth/login", json={
            "email": "mfa_tester@paypath.ai",
            "password": "SecurePassword2026!",
            "mfa_code": totp.now()
        })
        assert login_success_mfa.status_code == 200
        assert login_success_mfa.json()["access_token"] != ""
        new_token = login_success_mfa.json()["access_token"]

        # 7. Disable MFA requires valid TOTP code
        bad_disable = await client.post("/api/v1/auth/mfa/disable", json={"code": "111111"}, headers={"Authorization": f"Bearer {new_token}"})
        assert bad_disable.status_code == 400

        good_disable = await client.post("/api/v1/auth/mfa/disable", json={"code": totp.now()}, headers={"Authorization": f"Bearer {new_token}"})
        assert good_disable.status_code == 200
        assert good_disable.json()["mfa_enabled"] is False

@pytest.mark.asyncio
async def test_password_reset_replay_defense():
    """Verify that password reset tokens cannot be replayed after use."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Request reset
        req = await client.post("/api/v1/auth/password-reset/request", json={"email": "demo@paypath.finance"})
        assert req.status_code == 200
        token = req.json()["dev_reset_token"]

        # 1. First reset succeeds
        first_use = await client.post("/api/v1/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "NewStrongPassword123!"
        })
        assert first_use.status_code == 200

        # 2. Adversarial: Replaying the same token MUST fail
        replay_use = await client.post("/api/v1/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "AttackerHackedPassword!"
        })
        assert replay_use.status_code == 400
        assert "Invalid or expired" in replay_use.json()["detail"]

@pytest.mark.asyncio
async def test_idor_transaction_access_prevention():
    """Verify that User A cannot inspect User B's transactions or lifecycle events."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create User A
        reg_a = await client.post("/api/v1/auth/register", json={
            "email": "user_a@test.com", "password": "PasswordA123!"
        })
        user_a_id = reg_a.json()["id"]

        # Create User B
        reg_b = await client.post("/api/v1/auth/register", json={
            "email": "user_b@test.com", "password": "PasswordB123!"
        })
        token_b = (await client.post("/api/v1/auth/login", json={"email": "user_b@test.com", "password": "PasswordB123!"})).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User B attempts to access a transaction belonging to demo user (tx_nova_anc_hero)
        res = await client.get("/api/v1/transactions/tx_nova_anc_hero", headers=headers_b)
        assert res.status_code == 404

        # User B attempts to access events of demo user's transaction
        event_res = await client.get("/api/v1/transactions/tx_nova_anc_hero/events", headers=headers_b)
        assert event_res.status_code == 404

@pytest.mark.asyncio
async def test_rbac_merchant_operations_denial():
    """Verify that normal USER role is rejected from merchant management operations."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login as standard USER
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "demo@paypath.finance", "password": "NewStrongPassword123!"
        })
        if login_res.status_code != 200:
            login_res = await client.post("/api/v1/auth/login", json={
                "email": "demo@paypath.finance", "password": "paypath123!"
            })
        user_token = login_res.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Attempt to onboard merchant
        onboard_res = await client.post("/api/v1/merchants", json={
            "name": "Unauthorized Store", "slug": "unauth-store"
        }, headers=user_headers)
        assert onboard_res.status_code == 403

        # Attempt to upload policy
        upload_res = await client.post("/api/v1/merchants/mch_nova_electronics/policies", json={
            "title": "Malicious Policy", "content": "All items non-refundable"
        }, headers=user_headers)
        assert upload_res.status_code == 403

@pytest.mark.asyncio
async def test_financial_invariants_and_refund_boundaries():
    """Verify mathematical boundaries: negative refund, overflow refund, and idempotency conflicts."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        tx_id = "tx_nova_anc_hero" # $89.00 captured transaction

        # 1. Zero or negative refund
        neg_res = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": -10.00,
            "currency": "USD"
        })
        assert neg_res.status_code in [400, 422]

        # 2. Refund exceeding transaction balance ($89.00 item, attempting $500.00)
        overflow_res = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": 500.00,
            "currency": "USD"
        })
        assert overflow_res.status_code == 400
        assert "exceeds remaining refundable balance" in overflow_res.json()["detail"]

        # 3. Currency mismatch (transaction is USD, requesting EUR)
        curr_res = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": 20.00,
            "currency": "EUR"
        })
        assert curr_res.status_code == 400
        assert "Currency mismatch" in curr_res.json()["detail"]

        # 4. Valid partial refund with idempotency key
        idem_key = "idemp_test_adv_001"
        valid_res = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": 25.00,
            "currency": "USD"
        }, headers={"X-Idempotency-Key": idem_key})
        assert valid_res.status_code == 200
        assert valid_res.json()["status"] == "COMPLETED"

        # 5. Replay with identical key and identical amount -> Idempotent success (no duplicate)
        replay_same = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": 25.00,
            "currency": "USD"
        }, headers={"X-Idempotency-Key": idem_key})
        assert replay_same.status_code == 200
        assert replay_same.json()["refund_id"] == valid_res.json()["refund_id"]

        # 6. Replay with identical key but DIFFERENT amount -> 409 Conflict
        replay_diff = await client.post("/api/v1/paycore/refunds", json={
            "transaction_id": tx_id,
            "amount": 35.00,
            "currency": "USD"
        }, headers={"X-Idempotency-Key": idem_key})
        assert replay_diff.status_code == 409
        assert "Idempotency conflict" in replay_diff.json()["detail"]

