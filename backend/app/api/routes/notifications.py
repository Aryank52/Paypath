from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.api.deps import get_current_user
from app.core.providers.notification_provider import notification_service

router = APIRouter(prefix="/notifications", tags=["In-App Notifications & Alerts"])

class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    notification_type: str = "GENERAL"
    action_url: Optional[str] = None

@router.get("")
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(20)
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "action_url": n.action_url,
            "created_at": n.created_at
        } for n in notifications
    ]

@router.post("/send")
async def dispatch_notification(
    payload: CreateNotificationRequest,
    send_email: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = Notification(
        user_id=current_user.id,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        action_url=payload.action_url,
        is_read=False
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    # Dispatch via composite provider (In-App + Email adapter)
    delivery = await notification_service.notify(
        recipient=current_user.email,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        send_email=send_email
    )

    return {
        "id": notif.id,
        "status": "DELIVERED",
        "delivery": delivery
    }

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    n = (await db.execute(stmt)).scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found.")

    n.is_read = True
    await db.commit()
    return {"id": n.id, "is_read": True}

