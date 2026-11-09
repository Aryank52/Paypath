from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    generate_totp_secret, get_totp_uri, verify_totp_code,
    generate_password_reset_token, hash_reset_token, revoke_token
)
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse,
    MFASetupResponse, MFAVerifyRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.api.deps import get_current_user
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role or UserRole.USER,
        mfa_enabled=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated."
        )

    # Check MFA if enabled on user account
    if user.mfa_enabled:
        if not payload.mfa_code:
            return TokenResponse(
                access_token="",
                user_id=user.id,
                email=user.email,
                role=user.role.value if hasattr(user.role, 'value') else str(user.role),
                full_name=user.full_name,
                mfa_required=True
            )
        if not verify_totp_code(user.mfa_secret or "", payload.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA two-factor authentication code."
            )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role)
    )
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        mfa_required=False
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate TOTP secret and provisioning URI for Google Authenticator / Authy."""
    secret = generate_totp_secret()
    current_user.mfa_secret = secret
    await db.commit()
    
    otpauth_url = get_totp_uri(secret, current_user.email)
    return MFASetupResponse(
        secret=secret,
        otpauth_url=otpauth_url,
        message="Scan the QR code with your authenticator app, then call /auth/mfa/enable with the 6-digit code."
    )

@router.post("/mfa/enable")
async def enable_mfa(
    payload: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify code and formally activate MFA on user account."""
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA setup has not been initiated.")
    
    if not verify_totp_code(current_user.mfa_secret, payload.code):
        raise HTTPException(status_code=400, detail="Invalid verification code.")
    
    current_user.mfa_enabled = True
    await db.commit()
    return {"message": "Two-factor authentication successfully enabled.", "mfa_enabled": True}

@router.post("/mfa/disable")
async def disable_mfa(
    payload: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable MFA after verifying current TOTP code."""
    if not current_user.mfa_enabled:
        return {"message": "MFA is already disabled."}
    
    if not verify_totp_code(current_user.mfa_secret or "", payload.code):
        raise HTTPException(status_code=400, detail="Invalid verification code.")
    
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    await db.commit()
    return {"message": "Two-factor authentication disabled.", "mfa_enabled": False}

@router.post("/password-reset/request")
async def request_password_reset(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate secure password reset token."""
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        # Return generic message to prevent email enumeration
        return {"message": "If this email is registered, a password reset link has been dispatched."}
    
    raw_token, hashed_token, expires_at = generate_password_reset_token()
    user.password_reset_token = hashed_token
    user.password_reset_expires = expires_at
    await db.commit()

    return {
        "message": "If this email is registered, a password reset link has been dispatched.",
        "dev_reset_token": raw_token  # Provided for local dev / testing inspection
    }

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Verify reset token and update password."""
    hashed_token = hash_reset_token(payload.token)
    stmt = select(User).where(User.password_reset_token == hashed_token)
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    expires = user.password_reset_expires
    if expires:
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Password reset token has expired.")
    
    user.hashed_password = get_password_hash(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db.commit()

    return {"message": "Password successfully updated. You may now log in with your new credentials."}

@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Revoke current access token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        revoke_token(token)
    return {"message": "Successfully logged out."}
