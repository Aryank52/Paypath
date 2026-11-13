from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionEvent
from app.schemas.transaction import (
    TransactionResponse,
    TransactionEventResponse,
    SharedFeedResponse,
    SharedFeedItem
)
from app.api.deps import get_current_user, oauth2_scheme

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/feed", response_model=SharedFeedResponse)
async def get_transaction_feed(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page (max 100)"),
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH)"),
    search: Optional[str] = Query(None, description="Search merchant or item"),
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """
    Sanitized read-only transaction intelligence feed available to authenticated users.
    Backed by authoritative Render PostgreSQL transactions table.
    Enforces strict data sanitization: NO internal IDs, emails, PayPal IDs, or tenant secrets.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication token required to access transaction intelligence feed."
        )
    # Subquery to calculate deterministic sequential sequence number per transaction
    seq_subquery = select(
        Transaction.id.label("tx_id"),
        func.row_number().over(order_by=Transaction.created_at.asc()).label("seq_num")
    ).subquery()

    query = (
        select(Transaction, seq_subquery.c.seq_num)
        .join(seq_subquery, Transaction.id == seq_subquery.c.tx_id)
        .order_by(Transaction.created_at.desc())
    )

    count_query = select(func.count(Transaction.id))

    if status:
        query = query.where(Transaction.status == status)
        count_query = count_query.where(Transaction.status == status)
    if risk_level:
        query = query.where(Transaction.risk_level == risk_level)
        count_query = count_query.where(Transaction.risk_level == risk_level)
    if search:
        search_filter = or_(
            Transaction.merchant_name.ilike(f"%{search}%"),
            Transaction.item_description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_records = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    results = (await db.execute(query)).all()

    items = [
        SharedFeedItem(
            public_reference=f"PP-TRX-{seq_num:06d}",
            merchant_name=tx.merchant_name,
            item=tx.item_description or "General Order",
            amount=float(tx.amount),
            currency=tx.currency,
            payment_state=tx.status,
            risk_level=tx.risk_level,
            verification_status=tx.verification_status,
            source=tx.source_type,
            ai_summary=tx.ai_summary,
            created_at=tx.created_at
        )
        for tx, seq_num in results
    ]

    return SharedFeedResponse(
        total_records=total_records,
        page=page,
        limit=limit,
        items=items,
        provenance="RENDER_POSTGRESQL_16"
    )

@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH)"),
    merchant_name: Optional[str] = Query(None, description="Filter by merchant"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Transaction).order_by(Transaction.created_at.desc())

    # Role-based tenant and user scoping
    if current_user.role == UserRole.PLATFORM_ADMIN:
        # Platform administrators have authoritative platform-wide ledger visibility
        if merchant_name:
            stmt = stmt.where(Transaction.merchant_name == merchant_name)
    elif current_user.role in (UserRole.MERCHANT_ADMIN, UserRole.MERCHANT_USER):
        # Merchant administrators oversee transactions for their merchant store
        if merchant_name:
            stmt = stmt.where(Transaction.merchant_name == merchant_name)
        else:
            stmt = stmt.where(Transaction.user_id == current_user.id)
    else:
        # Shoppers have strict tenant boundary scoped to their own transactions
        stmt = stmt.where(Transaction.user_id == current_user.id)
        if merchant_name:
            stmt = stmt.where(Transaction.merchant_name == merchant_name)

    if status:
        stmt = stmt.where(Transaction.status == status)
    if risk_level:
        stmt = stmt.where(Transaction.risk_level == risk_level)

    result = await db.execute(stmt)
    transactions = result.scalars().all()
    return list(transactions)

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    if current_user.role != UserRole.PLATFORM_ADMIN:
        stmt = stmt.where(Transaction.user_id == current_user.id)
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
    # Verify transaction ownership or platform admin privilege to prevent IDOR information disclosure
    tx_stmt = select(Transaction).where(Transaction.id == transaction_id)
    if current_user.role != UserRole.PLATFORM_ADMIN:
        tx_stmt = tx_stmt.where(Transaction.user_id == current_user.id)
    tx = (await db.execute(tx_stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    stmt = select(TransactionEvent).where(TransactionEvent.transaction_id == transaction_id).order_by(TransactionEvent.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

