import pytest
from httpx import AsyncClient, ASGITransport
import io
from app.main import app
from app.core.security import generate_totp_secret, verify_totp_code
import pyotp

@pytest.mark.asyncio
async def test_mfa_lifecycle():
    secret = generate_totp_secret()
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()

    assert verify_totp_code(secret, valid_code) is True
    assert verify_totp_code(secret, "000000") is False

@pytest.mark.asyncio
async def test_password_reset_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Request password reset
        resp = await client.post("/api/v1/auth/password-reset/request", json={"email": "demo@paypath.finance"})
        assert resp.status_code == 200
        data = resp.json()
        assert "dev_reset_token" in data
        token = data["dev_reset_token"]

        # Confirm password reset
        confirm_resp = await client.post("/api/v1/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "NewPayPath2026!Secure"
        })
        assert confirm_resp.status_code == 200

        # Login with new password
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "demo@paypath.finance",
            "password": "NewPayPath2026!Secure"
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

@pytest.mark.asyncio
async def test_file_upload_security_magic_bytes():
    from app.core.upload_security import validate_and_save_upload
    from fastapi import UploadFile, HTTPException

    # 1. Valid JPEG with real magic bytes
    valid_jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    valid_file = UploadFile(
        file=io.BytesIO(valid_jpeg_bytes),
        filename="damage_proof.jpg",
        headers={"content-type": "image/jpeg"}
    )
    name, url, size, mime = await validate_and_save_upload(valid_file)
    assert mime == "image/jpeg"
    assert url.startswith("/uploads/evidence/")
    assert size > 0

    # 2. Fake extension (text/sh disguised as jpg)
    fake_bytes = b"#!/bin/bash\nrm -rf /"
    spoofed_file = UploadFile(
        file=io.BytesIO(fake_bytes),
        filename="exploit.jpg",
        headers={"content-type": "image/jpeg"}
    )
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_save_upload(spoofed_file)
    assert exc_info.value.status_code == 415

    # 3. Path traversal attack in filename
    traversal_file = UploadFile(
        file=io.BytesIO(valid_jpeg_bytes),
        filename="../../../etc/cron.d/malicious.jpg",
        headers={"content-type": "image/jpeg"}
    )
    safe_name, safe_url, _, _ = await validate_and_save_upload(traversal_file)
    assert ".." not in safe_name
    assert "malicious.jpg" in safe_name
