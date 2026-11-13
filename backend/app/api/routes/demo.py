from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, revoke_token
from app.models.user import User, UserRole
from app.schemas.auth import DemoSessionRequest, DemoSessionResponse
from app.api.deps import get_current_user, oauth2_scheme
from app.core.rate_limiter import rate_limit
from app.core.observability import logger, log_audit_event
from typing import Optional

router = APIRouter(prefix="/demo", tags=["Evaluator Demo"])

DEMO_PERSONA_EMAILS = {
    "shopper": "demo@paypath.finance",
    "merchant": "sarah.jenkins@paypath.finance",
    "platform_admin": "marcus.vance@paypath.finance"
}

ALLOWED_DEMO_PERSONAS = ["SHOPPER", "MERCHANT_ADMIN", "PLATFORM_ADMIN"]

@router.post("/session", response_model=DemoSessionResponse)
async def create_demo_session(
    payload: Optional[DemoSessionRequest] = None,
    db: AsyncSession = Depends(get_db),
    _limiter: bool = Depends(rate_limit(max_requests=30, window_seconds=60))
):
    """
    Public Evaluator Mode session creation for hackathon review.
    Enables judges to explore PayPath without manual registration or credential exchange.
    Creates a scoped, short-lived JWT with explicit demo claims.
    """
    if not settings.DEMO_MODE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo Evaluator Mode is currently disabled in this environment."
        )

    requested = (payload.persona if payload and payload.persona else "shopper").strip().lower()
    if requested in ("merchant_admin",):
        requested = "merchant"
    elif requested in ("control_center", "admin"):
        requested = "platform_admin"

    if requested not in DEMO_PERSONA_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid demo persona '{requested}'. Allowed: ['shopper', 'merchant', 'platform_admin']."
        )

    target_email = DEMO_PERSONA_EMAILS[requested]
    stmt = select(User).where(User.email == target_email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        # Fallback to any user matching role
        role_map = {
            "shopper": UserRole.USER,
            "merchant": UserRole.MERCHANT_ADMIN,
            "platform_admin": UserRole.PLATFORM_ADMIN
        }
        fallback_stmt = select(User).where(User.role == role_map[requested])
        user = (await db.execute(fallback_stmt)).scalars().first()
        if not user:
            raise HTTPException(status_code=500, detail=f"Demo identity for '{requested}' is not configured.")

    active_persona = requested.upper()
    if active_persona == "MERCHANT":
        active_persona = "MERCHANT_ADMIN"

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        extra_claims={
            "demo_mode": True,
            "demo_persona": active_persona
        }
    )

    log_audit_event(
        action="DEMO_SESSION_CREATED",
        actor_type="EVALUATOR",
        actor_id=user.id,
        resource_type="SESSION",
        resource_id=f"demo_{active_persona}",
        details={"persona": active_persona, "email": user.email}
    )

    return DemoSessionResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        active_persona=active_persona,
        allowed_personas=ALLOWED_DEMO_PERSONAS,
        full_name=user.full_name,
        is_demo=True
    )

@router.post("/switch", response_model=DemoSessionResponse)
async def switch_demo_persona(
    payload: DemoSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Seamless persona switching within Evaluator Demo Mode.
    Allows judges to navigate Shopper <-> Merchant <-> Control Center without re-entering credentials.
    """
    if not getattr(current_user, "is_demo", False) and current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo persona switching requires an active demo evaluator session."
        )

    requested = (payload.persona or "shopper").strip().lower()
    if requested in ("merchant_admin",):
        requested = "merchant"
    elif requested in ("control_center", "admin"):
        requested = "platform_admin"

    if requested not in DEMO_PERSONA_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid demo persona '{requested}'. Allowed: ['shopper', 'merchant', 'platform_admin']."
        )

    target_email = DEMO_PERSONA_EMAILS[requested]
    stmt = select(User).where(User.email == target_email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        role_map = {
            "shopper": UserRole.USER,
            "merchant": UserRole.MERCHANT_ADMIN,
            "platform_admin": UserRole.PLATFORM_ADMIN
        }
        user = (await db.execute(select(User).where(User.role == role_map[requested]))).scalars().first()
        if not user:
            raise HTTPException(status_code=500, detail=f"Target demo persona '{requested}' not found.")

    active_persona = requested.upper()
    if active_persona == "MERCHANT":
        active_persona = "MERCHANT_ADMIN"

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        extra_claims={
            "demo_mode": True,
            "demo_persona": active_persona
        }
    )

    log_audit_event(
        action="DEMO_PERSONA_SWITCHED",
        actor_type="EVALUATOR",
        actor_id=user.id,
        resource_type="SESSION",
        resource_id=f"demo_{active_persona}",
        details={"from_user": current_user.id, "to_persona": active_persona}
    )

    return DemoSessionResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        active_persona=active_persona,
        allowed_personas=ALLOWED_DEMO_PERSONAS,
        full_name=user.full_name,
        is_demo=True
    )

@router.post("/exit")
async def exit_demo_session(
    token: Optional[str] = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """Terminates evaluator demo session and revokes token."""
    if token:
        revoke_token(token)
    log_audit_event(
        action="DEMO_SESSION_EXITED",
        actor_type="EVALUATOR",
        actor_id=current_user.id,
        resource_type="SESSION",
        resource_id="demo_exit",
        details={"user_id": current_user.id}
    )
    return {"message": "Demo session exited and revoked successfully."}

