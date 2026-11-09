from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.paycore.service import PayCoreService
from app.paycore.verifier import payment_verifier
from app.schemas.paycore import (
    CreateOrderRequest,
    CreateOrderResponse,
    CaptureOrderRequest,
    CaptureOrderResponse,
    RefundRequest,
    RefundResponse,
    VerificationResultSchema
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/paycore", tags=["PayCore"])

@router.post("/orders/create", response_model=CreateOrderResponse)
async def create_order(
    payload: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = PayCoreService(db)
    result = await service.create_order(
        user_id=current_user.id,
        amount=payload.amount,
        currency=payload.currency,
        merchant_name=payload.merchant_name,
        merchant_id=payload.merchant_id,
        item_description=payload.item_description,
        user_intent_id=payload.user_intent_id
    )
    return CreateOrderResponse(
        order_id=result["order_id"],
        status=result["status"],
        approve_url=result["approve_url"],
        amount=result["amount"],
        currency=result["currency"]
    )

@router.post("/orders/capture", response_model=CaptureOrderResponse)
async def capture_order(
    payload: CaptureOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = PayCoreService(db)
    result = await service.capture_order(
        order_id=payload.order_id,
        user_id=current_user.id
    )
    return CaptureOrderResponse(
        transaction_id=result.get("transaction_id"),
        capture_id=result["capture_id"],
        order_id=result["order_id"],
        status=result["status"],
        amount=result["amount"],
        currency=result["currency"],
        verification_status=result["verification_status"]
    )

@router.post("/refunds", response_model=RefundResponse)
async def refund_payment(
    payload: RefundRequest,
    x_idempotency_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = PayCoreService(db)
    result = await service.execute_refund(
        transaction_id=payload.transaction_id,
        amount=payload.amount,
        currency=payload.currency,
        reason=payload.reason,
        idempotency_key=x_idempotency_key,
        actor_id=current_user.id
    )
    return RefundResponse(
        refund_id=result["refund_id"],
        capture_id=result["capture_id"],
        status=result["status"],
        amount=result["amount"],
        currency=result["currency"],
        verification_status=result["verification_status"],
        is_verified=result["is_verified"]
    )

@router.get("/verify/{resource_id}", response_model=VerificationResultSchema)
async def independent_verify(
    resource_id: str,
    action_type: str = Query("CAPTURE", pattern="^(CAPTURE|REFUND)$"),
    expected_amount: float = Query(...),
    expected_currency: str = Query("USD")
):
    if action_type == "REFUND":
        is_verified, details = await payment_verifier.verify_refund(
            refund_id=resource_id,
            expected_amount=expected_amount,
            expected_currency=expected_currency
        )
    else:
        is_verified, details = await payment_verifier.verify_capture(
            capture_id=resource_id,
            expected_amount=expected_amount,
            expected_currency=expected_currency
        )

    amount_obj = details.get("amount", {})
    actual_amount = float(amount_obj.get("value", expected_amount))
    actual_currency = amount_obj.get("currency_code", expected_currency)

    return VerificationResultSchema(
        is_verified=is_verified,
        resource_id=resource_id,
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        expected_currency=expected_currency,
        actual_currency=actual_currency,
        paypal_status=details.get("status", "COMPLETED"),
        details=details
    )
