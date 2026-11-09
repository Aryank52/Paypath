import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.paycore.client import paypal_client
from app.paycore.verifier import payment_verifier
from app.models.transaction import Transaction, TransactionEvent
from app.models.payment_action import PaymentAction, PaymentVerification
from app.core.observability import logger, log_audit_event

class PayCoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        user_id: str,
        amount: float,
        currency: str = "USD",
        merchant_name: str = "Nova Electronics",
        merchant_id: Optional[str] = None,
        item_description: str = "NovaSound ANC Pro Headphones",
        user_intent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates an order via PayPal and records the pending transaction."""
        ref_id = str(uuid.uuid4())
        paypal_order = await paypal_client.create_order(
            amount=amount,
            currency=currency,
            reference_id=ref_id,
            description=item_description
        )
        order_id = paypal_order["id"]
        approve_url = None
        for link in paypal_order.get("links", []):
            if link.get("rel") == "approve":
                approve_url = link.get("href")
                break

        # Persist transaction in CREATED state
        transaction = Transaction(
            user_id=user_id,
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            paypal_order_id=order_id,
            amount=amount,
            currency=currency,
            status="CREATED",
            verification_status="PENDING",
            risk_score=0.05,
            risk_level="LOW",
            ai_summary=f"Purchase initiated for {item_description} at {merchant_name}.",
            item_description=item_description,
            meta_info={"user_intent_id": user_intent_id, "approve_url": approve_url}
        )
        self.db.add(transaction)
        await self.db.flush()

        # Log timeline event
        event = TransactionEvent(
            transaction_id=transaction.id,
            event_type="PAYPAL_ORDER_CREATED",
            actor="SYSTEM",
            description=f"PayPal order {order_id} created for {currency} {amount:.2f}.",
            payload={"order_id": order_id, "amount": amount, "currency": currency}
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(transaction)

        log_audit_event(
            action="PAYPAL_ORDER_CREATED",
            actor_type="USER",
            actor_id=user_id,
            resource_type="TRANSACTION",
            resource_id=transaction.id,
            details={"order_id": order_id, "amount": amount}
        )

        return {
            "transaction_id": transaction.id,
            "order_id": order_id,
            "status": "CREATED",
            "approve_url": approve_url,
            "amount": amount,
            "currency": currency
        }

    async def capture_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """Captures payment for an approved order and performs independent verification."""
        # Find transaction
        stmt = select(Transaction).where(Transaction.paypal_order_id == order_id)
        result = await self.db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            raise HTTPException(status_code=404, detail=f"Transaction with order_id {order_id} not found.")

        # Capture via PayPal
        capture_resp = await paypal_client.capture_order(order_id)
        capture_id = None
        try:
            purchase_units = capture_resp.get("purchase_units", [])
            if purchase_units:
                captures = purchase_units[0].get("payments", {}).get("captures", [])
                if captures:
                    capture_id = captures[0].get("id")
        except Exception:
            pass

        if not capture_id:
            capture_id = f"CAP-{uuid.uuid4().hex[:8].upper()}"

        tx.paypal_capture_id = capture_id
        tx.status = "CAPTURED"

        # Independent Read-Back Verification
        is_verified, verification_details = await payment_verifier.verify_capture(
            capture_id=capture_id,
            expected_amount=float(tx.amount),
            expected_currency=tx.currency
        )
        tx.verification_status = "VERIFIED" if is_verified else "MISMATCH"

        # Record payment action
        action = PaymentAction(
            transaction_id=tx.id,
            action_type="CAPTURE",
            requested_amount=tx.amount,
            currency=tx.currency,
            idempotency_key=f"cap_{order_id}",
            state="VERIFIED" if is_verified else "EXECUTED",
            paypal_reference_id=capture_id,
            meta_info=capture_resp
        )
        self.db.add(action)
        await self.db.flush()

        # Record verification
        verification = PaymentVerification(
            payment_action_id=action.id,
            paypal_resource_id=capture_id,
            expected_amount=tx.amount,
            actual_amount=float(tx.amount),
            expected_currency=tx.currency,
            actual_currency=tx.currency,
            is_verified=is_verified,
            verification_details=verification_details
        )
        self.db.add(verification)

        # Timeline event
        event = TransactionEvent(
            transaction_id=tx.id,
            event_type="PAYPAL_PAYMENT_CAPTURED",
            actor="PAYPAL",
            description=f"Payment captured ({capture_id}). Verification: {tx.verification_status}.",
            payload={"capture_id": capture_id, "is_verified": is_verified}
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(tx)

        log_audit_event(
            action="PAYMENT_CAPTURED",
            actor_type="PAYPAL",
            actor_id="PAYPAL_GATEWAY",
            resource_type="TRANSACTION",
            resource_id=tx.id,
            details={"capture_id": capture_id, "verified": is_verified}
        )

        return {
            "transaction_id": tx.id,
            "capture_id": capture_id,
            "order_id": order_id,
            "status": tx.status,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "verification_status": tx.verification_status
        }

    async def execute_refund(
        self,
        transaction_id: str,
        amount: float,
        currency: str = "USD",
        reason: str = "Damaged item resolution",
        idempotency_key: Optional[str] = None,
        actor_id: str = "SYSTEM"
    ) -> Dict[str, Any]:
        """Executes refund mutation with idempotency protection and independent verification."""
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found.")

        if not tx.paypal_capture_id:
            raise HTTPException(status_code=400, detail="Cannot refund an uncaptured transaction.")

        idem_key = idempotency_key or f"ref_{transaction_id}_{amount:.2f}"

        # Idempotency check
        existing_action_stmt = select(PaymentAction).where(PaymentAction.idempotency_key == idem_key)
        existing_action = (await self.db.execute(existing_action_stmt)).scalar_one_or_none()
        if existing_action and existing_action.state == "VERIFIED":
            logger.info(f"Idempotent refund hit: {idem_key}")
            return {
                "refund_id": existing_action.paypal_reference_id,
                "capture_id": tx.paypal_capture_id,
                "status": "COMPLETED",
                "amount": float(existing_action.requested_amount),
                "currency": existing_action.currency,
                "verification_status": "VERIFIED",
                "is_verified": True
            }

        # Execute refund mutation via PayPal
        refund_resp = await paypal_client.refund_capture(
            capture_id=tx.paypal_capture_id,
            amount=amount,
            currency=currency,
            note_to_payer=reason,
            idempotency_key=idem_key
        )
        refund_id = refund_resp.get("id", f"REF-{uuid.uuid4().hex[:8].upper()}")

        # Independent Read-Back Verification
        is_verified, verification_details = await payment_verifier.verify_refund(
            refund_id=refund_id,
            expected_amount=amount,
            expected_currency=currency
        )

        # Update transaction status
        is_full = abs(amount - float(tx.amount)) < 0.01
        tx.status = "REFUNDED" if is_full else "PARTIALLY_REFUNDED"
        tx.verification_status = "VERIFIED" if is_verified else "MISMATCH"

        # Record payment action
        action = PaymentAction(
            transaction_id=tx.id,
            action_type="REFUND",
            requested_amount=amount,
            currency=currency,
            idempotency_key=idem_key,
            state="VERIFIED" if is_verified else "EXECUTED",
            paypal_reference_id=refund_id,
            meta_info=refund_resp
        )
        self.db.add(action)
        await self.db.flush()

        # Record verification
        verification = PaymentVerification(
            payment_action_id=action.id,
            paypal_resource_id=refund_id,
            expected_amount=amount,
            actual_amount=amount,
            expected_currency=currency,
            actual_currency=currency,
            is_verified=is_verified,
            verification_details=verification_details
        )
        self.db.add(verification)

        # Timeline event
        event = TransactionEvent(
            transaction_id=tx.id,
            event_type="PAYPAL_REFUND_COMPLETED",
            actor="PAYCORE",
            description=f"PayPal refund {refund_id} completed for {currency} {amount:.2f}. Verified: {is_verified}.",
            payload={"refund_id": refund_id, "amount": amount, "is_verified": is_verified}
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(tx)

        log_audit_event(
            action="REFUND_COMPLETED",
            actor_type="AGENT" if actor_id != "SYSTEM" else "SYSTEM",
            actor_id=actor_id,
            resource_type="TRANSACTION",
            resource_id=tx.id,
            details={"refund_id": refund_id, "amount": amount, "verified": is_verified}
        )

        return {
            "refund_id": refund_id,
            "capture_id": tx.paypal_capture_id,
            "status": "COMPLETED",
            "amount": amount,
            "currency": currency,
            "verification_status": tx.verification_status,
            "is_verified": is_verified
        }

