import json
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta

from app.main import app
from app.paycore.webhook_verifier import create_test_webhook_signed_payload, PayPalWebhookVerifier
from app.core.config import settings
from app.paycore.client import paypal_client

@pytest.fixture(autouse=True)
def setup_webhook_test_env():
    # Set known test webhook ID in settings
    orig = getattr(settings, "PAYPAL_WEBHOOK_ID", "")
    settings.PAYPAL_WEBHOOK_ID = "WH-SECURE-TEST-WEBHOOK-99"
    yield
    settings.PAYPAL_WEBHOOK_ID = orig

@pytest.mark.asyncio
async def test_webhook_missing_headers():
    """Missing any of the 5 required PayPal headers returns HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-MISSING-HDRS-1", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        res = await client.post("/api/v1/paycore/webhooks/paypal", json=payload, headers={})
        assert res.status_code == 400
        assert "Missing required PayPal webhook headers" in res.json()["detail"]

@pytest.mark.asyncio
async def test_webhook_invalid_cert_url():
    """Cert URL hosted outside paypal.com or using insecure scheme returns HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-BAD-URL-1", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99",
            cert_url="https://attacker.com/v1/notifications/certs/evil.pem"
        )
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=raw_body,
            headers=headers
        )
        assert res.status_code == 400
        assert "Untrusted certificate URL host" in res.json()["detail"]

@pytest.mark.asyncio
async def test_webhook_expired_timestamp():
    """Transmission timestamp older than max age window returns HTTP 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-EXPIRED-TS-1", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99",
            transmission_time=old_time
        )
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=raw_body,
            headers=headers
        )
        assert res.status_code == 401
        assert "timestamp expired" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    """Corrupted signature returns HTTP 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-BAD-SIG-1", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99"
        )
        # Corrupt the signature header
        headers["PAYPAL-TRANSMISSION-SIG"] = "bm90X2FfdmFsaWRfc2lnbmF0dXJl"
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=raw_body,
            headers=headers
        )
        assert res.status_code == 401
        assert "invalid" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_webhook_modified_payload():
    """Tampering with the payload body after signing invalidates CRC32/RSA and returns HTTP 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-TAMPER-1", "event_type": "PAYMENT.CAPTURE.COMPLETED", "amount": 50.0}
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99"
        )
        # Tamper body
        tampered_body = json.dumps({"id": "WH-TAMPER-1", "event_type": "PAYMENT.CAPTURE.COMPLETED", "amount": 5000.0}).encode('utf-8')
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=tampered_body,
            headers=headers
        )
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_webhook_wrong_webhook_id():
    """Payload signed for a different webhook ID fails signature check (401)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id": "WH-WRONG-ID-1", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-DIFFERENT-UNAUTHORIZED-ID"
        )
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=raw_body,
            headers=headers
        )
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_webhook_missing_event_id():
    """Payload missing required 'id' attribute returns HTTP 400 (never generates fake UUID)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"event_type": "PAYMENT.CAPTURE.COMPLETED", "resource": {"id": "CAP-123"}}
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99"
        )
        res = await client.post(
            "/api/v1/paycore/webhooks/paypal",
            content=raw_body,
            headers=headers
        )
        assert res.status_code == 400
        assert "missing event 'id'" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_webhook_valid_event_and_deduplication():
    """Valid signed webhook processes correctly, and duplicate event is idempotently ignored."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id": "WH-VALID-DEDUP-001",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAP-DEDUP-001",
                "amount": {"value": "89.00", "currency_code": "USD"},
                "supplementary_data": {"related_ids": {"order_id": "ORD-DEDUP-001"}}
            }
        }
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99",
            transmission_id="tx_dedup_unique_001"
        )

        # 1. First delivery
        r1 = await client.post("/api/v1/paycore/webhooks/paypal", content=raw_body, headers=headers)
        assert r1.status_code == 200
        assert r1.json()["status"] in ["VERIFIED", "PROCESSED", "RECONCILIATION_REQUIRED"]

        # 2. Duplicate delivery with same event ID
        r2 = await client.post("/api/v1/paycore/webhooks/paypal", content=raw_body, headers=headers)
        assert r2.status_code == 200
        assert r2.json()["status"] == "IGNORED"
        assert r2.json()["reason"] == "DUPLICATE_EVENT"

@pytest.mark.asyncio
async def test_webhook_duplicate_transmission_id():
    """Different event ID but duplicate transmission ID is idempotently ignored."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload1 = {"id": "WH-TX-ID-A", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        raw1, headers1 = create_test_webhook_signed_payload(
            payload1,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99",
            transmission_id="tx_shared_trans_999"
        )
        r1 = await client.post("/api/v1/paycore/webhooks/paypal", content=raw1, headers=headers1)
        assert r1.status_code == 200

        # Second payload with different event ID but same transmission ID
        payload2 = {"id": "WH-TX-ID-B", "event_type": "PAYMENT.CAPTURE.COMPLETED"}
        raw2, headers2 = create_test_webhook_signed_payload(
            payload2,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99",
            transmission_id="tx_shared_trans_999"
        )
        r2 = await client.post("/api/v1/paycore/webhooks/paypal", content=raw2, headers=headers2)
        assert r2.status_code == 200
        assert r2.json()["status"] == "IGNORED"
        assert r2.json()["reason"] == "DUPLICATE_TRANSMISSION"

@pytest.mark.asyncio
async def test_webhook_unknown_event_type():
    """Authenticated unknown event types are safely persisted without financial side-effects."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id": "WH-UNKNOWN-EVENT-001",
            "event_type": "BILLING.PLAN.CREATED",
            "resource": {"id": "P-9999"}
        }
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99"
        )
        res = await client.post("/api/v1/paycore/webhooks/paypal", content=raw_body, headers=headers)
        assert res.status_code == 200
        assert res.json()["status"] == "PROCESSED_UNHANDLED"

@pytest.mark.asyncio
async def test_webhook_capture_reconciliation_mismatch():
    """When independent read-back reveals amount/currency mismatch, status is RECONCILIATION_REQUIRED."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a real order & capture in db first to simulate transaction
        login_res = await client.post("/api/v1/auth/login", json={"email": "demo@paypath.finance", "password": "paypath123!"})
        token = login_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        order_res = await client.post("/api/v1/paycore/orders/create", json={
            "amount": 89.00,
            "currency": "USD",
            "merchant_name": "Nova Electronics",
            "item_description": "NovaSound ANC Test Headphones"
        }, headers=auth_headers)
        order_id = order_res.json()["order_id"]

        # Mock PayPal capture details with a mismatched amount (e.g. 10.00 instead of 89.00)
        capture_id = f"CAP-MISMATCH-{order_id}"
        paypal_client._mock_captures[capture_id] = {
            "id": capture_id,
            "status": "COMPLETED",
            "amount": {"value": "10.00", "currency_code": "USD"}  # Mismatch!
        }

        # Send Webhook with this capture ID
        payload = {
            "id": f"WH-MISMATCH-EVENT-{order_id}",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": capture_id,
                "amount": {"value": "10.00", "currency_code": "USD"},
                "supplementary_data": {"related_ids": {"order_id": order_id}}
            }
        }
        raw_body, headers = create_test_webhook_signed_payload(
            payload,
            webhook_id="WH-SECURE-TEST-WEBHOOK-99"
        )

        res = await client.post("/api/v1/paycore/webhooks/paypal", content=raw_body, headers=headers)
        assert res.status_code == 200
        # Independent read-back must flag RECONCILIATION_REQUIRED instead of blindly marking VERIFIED!
        assert res.json()["status"] == "RECONCILIATION_REQUIRED"
