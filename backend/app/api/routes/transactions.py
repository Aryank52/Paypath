from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionEvent
from app.schemas.transaction import TransactionResponse, TransactionEventResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH)"),
    merchant_name: Optional[str] = Query(None, description="Filter by merchant"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.created_at.desc())
    if status:
        stmt = stmt.where(Transaction.status == status)
    if risk_level:
        stmt = stmt.where(Transaction.risk_level == risk_level)
    if merchant_name:
        stmt = stmt.where(Transaction.merchant_name == merchant_name)

    result = await db.execute(stmt)
    transactions = result.scalars().all()
    return list(transactions)

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Fetch events
    event_stmt = select(TransactionEvent).where(TransactionEvent.transaction_id == tx.id).order_by(TransactionEvent.created_at.asc())
    event_result = await db.execute(event_stmt)
    events = event_result.scalars().all()

    tx_dict = {
        "id": tx.id,
        "user_id": tx.user_id,
        "merchant_id": tx.merchant_id,
        "merchant_name": tx.merchant_name,
        "paypal_order_id": tx.paypal_order_id,
        "paypal_capture_id": tx.paypal_capture_id,
        "amount": float(tx.amount),
        "currency": tx.currency,
        "status": tx.status,
        "verification_status": tx.verification_status,
        "risk_score": float(tx.risk_score),
        "risk_level": tx.risk_level,
        "source_type": tx.source_type,
        "ai_summary": tx.ai_summary,
        "item_description": tx.item_description,
        "meta_info": tx.meta_info,
        "created_at": tx.created_at,
        "events": list(events)
    }
    return tx_dict

@router.get("/{transaction_id}/events", response_model=List[TransactionEventResponse])
async def get_transaction_events(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify transaction ownership to prevent IDOR information disclosure
    tx_stmt = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    tx = (await db.execute(tx_stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    stmt = select(TransactionEvent).where(TransactionEvent.transaction_id == transaction_id).order_by(TransactionEvent.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

