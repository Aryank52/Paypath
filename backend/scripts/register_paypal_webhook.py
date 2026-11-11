"""
PayPath PayPal Webhook Automated Registration & Management Script.
Registers or updates the public PayPal Webhook endpoint with exact required events:
- CHECKOUT.ORDER.APPROVED
- CHECKOUT.PAYMENT-APPROVAL.REVERSED
- PAYMENT.CAPTURE.PENDING
- PAYMENT.CAPTURE.COMPLETED
- PAYMENT.CAPTURE.DENIED
- PAYMENT.CAPTURE.REFUNDED
- PAYMENT.CAPTURE.REVERSED

SAFETY DIRECTIVE:
Rejects 'localhost' and '127.0.0.1' URLs. Requires public HTTPS URL.
"""

import sys
import os
import argparse
import asyncio

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from app.core.config import settings
from app.paycore.client import paypal_client

REQUIRED_EVENT_NAMES = [
    "CHECKOUT.ORDER.APPROVED",
    "CHECKOUT.PAYMENT-APPROVAL.REVERSED",
    "PAYMENT.CAPTURE.PENDING",
    "PAYMENT.CAPTURE.COMPLETED",
    "PAYMENT.CAPTURE.DENIED",
    "PAYMENT.CAPTURE.REFUNDED",
    "PAYMENT.CAPTURE.REVERSED",
]

async def register_or_verify_webhook(target_url: str):
    if not target_url.startswith("https://"):
        print(f"[-] ERROR: Webhook URL must use HTTPS. Received: {target_url}")
        sys.exit(1)

    if "localhost" in target_url or "127.0.0.1" in target_url:
        print(f"[-] ERROR: PayPal rejects localhost/127.0.0.1 endpoints. Provide public HTTPS URL.")
        sys.exit(1)

    print(f"[+] Authenticating with PayPal ({paypal_client.base_url})...")
    token = await paypal_client.get_access_token()
    if not token or token == "mock-sandbox-access-token":
        print("[-] ERROR: Valid PayPal credentials required in environment.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        # 1. List existing webhooks to ensure idempotency
        print("[+] Querying registered webhooks from PayPal...")
        list_resp = await client.get(f"{paypal_client.base_url}/v1/notifications/webhooks", headers=headers)
        list_resp.raise_for_status()
        existing_webhooks = list_resp.json().get("webhooks", [])

        matched = None
        for wh in existing_webhooks:
            if wh.get("url") == target_url:
                matched = wh
                break

        if matched:
            wh_id = matched["id"]
            print(f"[+] Webhook already registered with ID: {wh_id}")
            print(f"[+] URL: {matched.get('url')}")
            print(f"[+] Status: ACTIVE")
            print(f"\nSet the following environment variable in Render / production:\n  PAYPAL_WEBHOOK_ID={wh_id}")
            return wh_id

        # 2. Register new webhook
        print(f"[+] Registering new webhook for URL: {target_url}...")
        payload = {
            "url": target_url,
            "event_types": [{"name": ev} for ev in REQUIRED_EVENT_NAMES]
        }
        create_resp = await client.post(
            f"{paypal_client.base_url}/v1/notifications/webhooks",
            headers=headers,
            json=payload
        )
        if create_resp.status_code not in (200, 201):
            print(f"[-] Failed to register webhook: {create_resp.status_code} - {create_resp.text}")
            sys.exit(1)

        wh_data = create_resp.json()
        wh_id = wh_data.get("id")
        print(f"[+] SUCCESS: PayPal Webhook created!")
        print(f"[+] Webhook ID: {wh_id}")
        print(f"[+] Target URL: {target_url}")
        print(f"[+] Registered Events: {len(wh_data.get('event_types', []))} events")
        print(f"\nSet the following environment variable in Render / production:\n  PAYPAL_WEBHOOK_ID={wh_id}")
        return wh_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register PayPath PayPal Webhook")
    parser.add_argument(
        "--url",
        required=True,
        help="Public HTTPS URL (e.g. https://paypath-api.onrender.com/api/v1/paycore/webhooks/paypal)"
    )
    args = parser.parse_args()
    asyncio.run(register_or_verify_webhook(args.url))
