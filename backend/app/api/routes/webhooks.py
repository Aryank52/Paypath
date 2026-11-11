import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.transaction import Transaction, TransactionEvent
from app.models.webhook import WebhookEvent
from app.core.observability import logger, log_audit_event
from app.core.rate_limiter import rate_limit
from app.paycore.webhook_verifier import PayPalWebhookVerifier, PayPalWebhookVerificationError
from app.paycore.verifier import payment_verifier
from app.paycore.client import paypal_client

router = APIRouter(prefix="/paycore/webhooks", tags=["PayPal Webhooks Ingestion"])

def sanitize_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Redacts any potential authorization, tokens, or credentials from webhook payloads."""
    sensitive_keys = {"client_secret", "password", "token", "authorization", "secret", "cookie"}
    def _redact(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: ("***REDACTED***" if any(s in k.lower() for s in sensitive_keys) else _redact(v))
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_redact(item) for item in obj]
        return obj
    return _redact(payload)

@router.post("/paypal")
async def handle_paypal_webhook(
    request: Request,
    paypal_auth_algo: Optional[str] = Header(None, alias="PAYPAL-AUTH-ALGO"),
    paypal_transmission_id: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-ID"),
    paypal_cert_url: Optional[str] = Header(None, alias="PAYPAL-CERT-URL"),
    paypal_transmission_sig: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-SIG"),
    paypal_transmission_time: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-TIME"),
    db: AsyncSession = Depends(get_db),
    _limiter: bool = Depends(rate_limit(max_requests=60, window_seconds=60))
):
    """
    Production-Hardened, Cryptographically Verified, Idempotent PayPal Webhook Receiver.

    Architecture Lifecycle:
    1. Read exact raw request body bytes (preserves CRC32 precision for RSA verification)
    2. Validate required PayPal headers (missing headers -> HTTP 400)
    3. Validate cert URL to prevent SSRF (untrusted host/path -> HTTP 400)
    4. Validate transmission timestamp for replay protection (expired/future -> HTTP 401)
    5. Authenticate cryptographic signature (self-verification or PayPal verification API)
    6. Validate event ID presence (never auto-generate UUID for missing ID)
    7. Deduplicate against PostgreSQL webhook_events table (idempotent 200 on duplicates)
    8. Execute state transitions:
       WEBHOOK_RECEIVED -> WEBHOOK_AUTHENTICATED -> RECONCILIATION_REQUIRED -> PAYPAL_READ_BACK -> VERIFIED
    9. Independently read back PayPal resource before marking transaction VERIFIED
    10. Log structured audit event and record sanitized payload
    """
    start_time = time.time()

    # 1. Read raw body bytes
    raw_body = await request.body()
    if not raw_body:
        raise HTTPException(status_code=400, detail="Empty request body.")
    payload_hash = hashlib.sha256(raw_body).hexdigest()

    auth_algo = paypal_auth_algo
    cert_url = paypal_cert_url
    transmission_id = paypal_transmission_id
    transmission_sig = paypal_transmission_sig
    transmission_time = paypal_transmission_time

    # 2. Validate required headers
    try:
        PayPalWebhookVerifier.validate_headers(
            auth_algo=auth_algo,
            cert_url=cert_url,
            transmission_id=transmission_id,
            transmission_sig=transmission_sig,
            transmission_time=transmission_time,
        )
    except PayPalWebhookVerificationError as e:
        logger.warning(f"PayPal webhook rejected: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # After validate_headers succeeds, all 5 headers are guaranteed non-empty strings
    assert auth_algo is not None
    assert cert_url is not None
    assert transmission_id is not None
    assert transmission_sig is not None
    assert transmission_time is not None

    # 3. Validate cert URL to neutralize SSRF
    try:
        PayPalWebhookVerifier.validate_cert_url(cert_url)
    except PayPalWebhookVerificationError as e:
        logger.warning(f"PayPal webhook cert URL rejected: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # 4. Validate transmission timestamp for replay protection
    try:
        PayPalWebhookVerifier.validate_timestamp(transmission_time)
    except PayPalWebhookVerificationError as e:
        logger.warning(f"PayPal webhook timestamp rejected: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # 5. Cryptographic signature verification
    try:
        await PayPalWebhookVerifier.verify_signature(
            raw_body=raw_body,
            auth_algo=auth_algo,
            cert_url=cert_url,
            transmission_id=transmission_id,
            transmission_sig=transmission_sig,
            transmission_time=transmission_time,
        )
    except PayPalWebhookVerificationError as e:
        # Fallback to PayPal API verification if configured
        try:
            body_json_tmp = json.loads(raw_body.decode("utf-8"))
        except Exception:
            raise HTTPException(status_code=400, detail="Malformed JSON in webhook body.")

        api_verified = await PayPalWebhookVerifier.verify_via_api(
            auth_algo=auth_algo,
            cert_url=cert_url,
            transmission_id=transmission_id,
            transmission_sig=transmission_sig,
            transmission_time=transmission_time,
            body_json=body_json_tmp
        )
        if not api_verified:
            logger.warning(f"PayPal webhook signature verification failed: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)

    # 6. Parse JSON payload and validate required fields
    try:
        body = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON payload.")

    event_id = body.get("id")
    if not event_id or not isinstance(event_id, str) or not event_id.strip():
        raise HTTPException(status_code=400, detail="Invalid webhook payload: missing event 'id'.")

    event_type = body.get("event_type", "UNKNOWN_EVENT")
    resource_type = body.get("resource_type")
    resource = body.get("resource", {})

    # 7. Database Deduplication & Idempotency check via PostgreSQL webhook_events table
    stmt_event = select(WebhookEvent).where(WebhookEvent.paypal_event_id == event_id)
    existing_event = (await db.execute(stmt_event)).scalar_one_or_none()
    if existing_event:
        logger.info(f"Duplicate webhook event ignored: {event_id} ({event_type})")
        return {
            "status": "IGNORED",
            "reason": "DUPLICATE_EVENT",
            "event_id": event_id,
            "event_type": event_type
        }

    # Check for duplicate transmission ID if provided
    if paypal_transmission_id:
        stmt_tx = select(WebhookEvent).where(WebhookEvent.transmission_id == paypal_transmission_id)
        existing_tx = (await db.execute(stmt_tx)).scalar_one_or_none()
        if existing_tx and existing_tx.status in ["VERIFIED", "PROCESSED", "IGNORED"]:
            logger.info(f"Duplicate transmission ID ignored: {paypal_transmission_id} ({event_type})")
            return {
                "status": "IGNORED",
                "reason": "DUPLICATE_TRANSMISSION",
                "transmission_id": paypal_transmission_id,
                "event_type": event_type
            }

    # 8. Record initial authenticated webhook in PostgreSQL
    sanitized_payload = sanitize_webhook_payload(body)
    webhook_record = WebhookEvent(
        paypal_event_id=event_id,
        transmission_id=paypal_transmission_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource.get("id"),
        status="WEBHOOK_AUTHENTICATED",
        received_at=datetime.now(timezone.utc),
        payload_hash=payload_hash,
        payload=sanitized_payload
    )
    db.add(webhook_record)
    await db.commit()
    await db.refresh(webhook_record)

    # 9. Process event with Independent PayPal Read-Back
    tx: Optional[Transaction] = None
    verification_outcome = "PROCESSED"
    processing_error = None

    try:
        if event_type in ["PAYMENT.CAPTURE.COMPLETED"]:
            capture_id = resource.get("id")
            order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
            amount_val = float(resource.get("amount", {}).get("value", 0.0))
            currency_code = resource.get("amount", {}).get("currency_code", "USD")

            # Find matching transaction by capture_id or order_id
            stmt = select(Transaction).where(
                (Transaction.paypal_capture_id == capture_id) | (Transaction.paypal_order_id == order_id)
            )
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx and capture_id:
                webhook_record.transaction_id = tx.id
                tx.verification_status = "RECONCILIATION_REQUIRED"
                await db.flush()

                # Perform independent read-back against PayPal capture resource
                is_verified, capture_details = await payment_verifier.verify_capture(
                    capture_id=capture_id,
                    expected_amount=float(tx.amount),
                    expected_currency=tx.currency
                )

                if is_verified:
                    tx.status = "CAPTURED"
                    tx.paypal_capture_id = capture_id
                    tx.verification_status = "VERIFIED"
                    verification_outcome = "VERIFIED"
                    event_desc = f"PayPal webhook capture verified for order {order_id or tx.paypal_order_id} via independent read-back."
                else:
                    tx.status = "CAPTURED"
                    tx.verification_status = "RECONCILIATION_REQUIRED"
                    verification_outcome = "RECONCILIATION_REQUIRED"
                    processing_error = f"Capture read-back mismatch: {capture_details}"
                    event_desc = (
                        f"PayPal webhook capture reconciliation required: amount/currency mismatch "
                        f"(claimed: {amount_val} {currency_code}, expected: {tx.amount} {tx.currency})."
                    )

                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_CAPTURE_CONFIRMED" if is_verified else "WEBHOOK_RECONCILIATION_REQUIRED",
                    actor="PAYPAL_WEBHOOK",
                    description=event_desc,
                    payload={
                        "capture_id": capture_id,
                        "is_verified": is_verified,
                        "claimed_amount": amount_val,
                        "claimed_currency": currency_code,
                        "details": capture_details,
                    }
                )
                db.add(event)

        elif event_type in ["PAYMENT.CAPTURE.REFUNDED"]:
            refund_id = resource.get("id")
            capture_id = None
            for link in resource.get("links", []):
                if link.get("rel") == "up":
                    capture_id = link.get("href", "").rstrip("/").split("/")[-1]
                    break
            if not capture_id:
                capture_id = resource.get("capture_id")

            refund_amount = float(resource.get("amount", {}).get("value", 0.0))
            refund_currency = resource.get("amount", {}).get("currency_code", "USD")

            stmt = select(Transaction).where(Transaction.paypal_capture_id == capture_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx and refund_id:
                webhook_record.transaction_id = tx.id
                tx.verification_status = "RECONCILIATION_REQUIRED"
                await db.flush()

                # Perform independent read-back of refund resource
                is_verified, refund_details = await payment_verifier.verify_refund(
                    refund_id=refund_id,
                    expected_amount=refund_amount,
                    expected_currency=refund_currency
                )

                if is_verified:
                    tx.status = "REFUNDED" if abs(refund_amount - float(tx.amount)) < 0.01 else "PARTIALLY_REFUNDED"
                    tx.verification_status = "VERIFIED"
                    verification_outcome = "VERIFIED"
                    event_desc = f"PayPal webhook refund verified for capture {capture_id} via independent read-back."
                else:
                    tx.verification_status = "RECONCILIATION_REQUIRED"
                    verification_outcome = "RECONCILIATION_REQUIRED"
                    processing_error = f"Refund read-back mismatch: {refund_details}"
                    event_desc = f"PayPal webhook refund reconciliation required: mismatch on refund {refund_id}."

                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_REFUND_CONFIRMED" if is_verified else "WEBHOOK_RECONCILIATION_REQUIRED",
                    actor="PAYPAL_WEBHOOK",
                    description=event_desc,
                    payload={"refund_id": refund_id, "is_verified": is_verified, "details": refund_details}
                )
                db.add(event)

        elif event_type in ["CHECKOUT.ORDER.APPROVED"]:
            order_id = resource.get("id")
            stmt = select(Transaction).where(Transaction.paypal_order_id == order_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx:
                webhook_record.transaction_id = tx.id
                # Read-back order state from PayPal
                order_details = await paypal_client.get_order_details(order_id)
                order_status = order_details.get("status")
                if order_status in ["APPROVED", "COMPLETED"]:
                    tx.status = "APPROVED"
                    tx.verification_status = "PENDING_CAPTURE"
                    verification_outcome = "VERIFIED"
                else:
                    tx.verification_status = "RECONCILIATION_REQUIRED"
                    verification_outcome = "RECONCILIATION_REQUIRED"
                    processing_error = f"Order status mismatch: {order_status}"

                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_ORDER_APPROVED",
                    actor="PAYPAL_WEBHOOK",
                    description=f"PayPal order {order_id} approved by buyer.",
                    payload=order_details
                )
                db.add(event)

        elif event_type in ["CHECKOUT.PAYMENT-APPROVAL.REVERSED"]:
            order_id = resource.get("id")
            stmt = select(Transaction).where(Transaction.paypal_order_id == order_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx:
                webhook_record.transaction_id = tx.id
                tx.status = "APPROVAL_REVERSED"
                tx.verification_status = "REVERSED"
                verification_outcome = "VERIFIED"
                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_ORDER_APPROVAL_REVERSED",
                    actor="PAYPAL_WEBHOOK",
                    description=f"PayPal order {order_id} buyer approval was reversed.",
                    payload=resource
                )
                db.add(event)

        elif event_type in ["PAYMENT.CAPTURE.DENIED"]:
            capture_id = resource.get("id")
            stmt = select(Transaction).where(Transaction.paypal_capture_id == capture_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx:
                webhook_record.transaction_id = tx.id
                tx.status = "CAPTURE_DENIED"
                tx.verification_status = "DENIED"
                verification_outcome = "VERIFIED"
                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_CAPTURE_DENIED",
                    actor="PAYPAL_WEBHOOK",
                    description=f"PayPal capture {capture_id} was denied.",
                    payload=resource
                )
                db.add(event)

        elif event_type in ["PAYMENT.CAPTURE.PENDING"]:
            capture_id = resource.get("id")
            stmt = select(Transaction).where(Transaction.paypal_capture_id == capture_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx:
                webhook_record.transaction_id = tx.id
                tx.status = "CAPTURE_PENDING"
                tx.verification_status = "PENDING"
                verification_outcome = "PROCESSED"
                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_CAPTURE_PENDING",
                    actor="PAYPAL_WEBHOOK",
                    description=f"PayPal capture {capture_id} is pending.",
                    payload=resource
                )
                db.add(event)

        elif event_type in ["PAYMENT.CAPTURE.REVERSED"]:
            capture_id = resource.get("id")
            stmt = select(Transaction).where(Transaction.paypal_capture_id == capture_id)
            tx = (await db.execute(stmt)).scalar_one_or_none()
            if tx:
                webhook_record.transaction_id = tx.id
                tx.status = "REVERSED"
                tx.verification_status = "REVERSED"
                verification_outcome = "VERIFIED"
                event = TransactionEvent(
                    transaction_id=tx.id,
                    event_type="WEBHOOK_CAPTURE_REVERSED",
                    actor="PAYPAL_WEBHOOK",
                    description=f"PayPal capture {capture_id} was reversed.",
                    payload=resource
                )
                db.add(event)

        else:
            # Unhandled / unknown event type: safely persist without mutation
            logger.info(f"Authenticated unhandled PayPal webhook event: {event_type} ({event_id})")
            verification_outcome = "PROCESSED_UNHANDLED"

    except Exception as exc:
        logger.error(f"Error executing webhook handler for {event_id}: {exc}", exc_info=True)
        verification_outcome = "FAILED"
        processing_error = str(exc)

    # 10. Update Webhook record in database
    webhook_record.status = verification_outcome
    webhook_record.processed_at = datetime.now(timezone.utc)
    webhook_record.processing_error = processing_error
    await db.commit()

    duration_ms = (time.time() - start_time) * 1000

    # 11. Audit log without sensitive credentials
    log_audit_event(
        action="WEBHOOK_PROCESSED",
        actor_type="PAYPAL_WEBHOOK",
        actor_id=event_id,
        resource_type="WEBHOOK_EVENT",
        resource_id=event_id,
        details={
            "event_type": event_type,
            "status": verification_outcome,
            "duration_ms": round(duration_ms, 2),
            "transaction_id": tx.id if tx else None,
            "transmission_id": paypal_transmission_id
        }
    )

    logger.info(
        f"PayPal webhook completed: id={event_id} type={event_type} "
        f"status={verification_outcome} duration={duration_ms:.1f}ms tx={tx.id if tx else 'N/A'}"
    )

    return {
        "status": verification_outcome,
        "event_id": event_id,
        "event_type": event_type,
        "transaction_id": tx.id if tx else None
    }
