from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.services.recovery_service import RecoveryService
from app.api.deps import get_current_user

router = APIRouter(prefix="/recover", tags=["Payment Recovery Intelligence"])

@router.get("/duplicates")
async def get_duplicate_signals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RecoveryService(db)
    duplicates = await service.detect_duplicates(current_user.id)
    return duplicates

@router.get("/subscriptions")
async def get_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RecoveryService(db)
    subs = await service.list_subscriptions(current_user.id)
    return [
        {
            "id": s.id,
            "merchant_name": s.merchant_name,
            "amount": float(s.amount),
            "currency": s.currency,
            "billing_interval": s.billing_interval,
            "last_payment_date": s.last_payment_date,
            "next_expected_date": s.next_expected_date,
            "status": s.status
        } for s in subs
    ]
