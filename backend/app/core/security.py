from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import secrets
import hashlib
import bcrypt
import pyotp
from jose import jwt
from app.core.config import settings

ALGORITHM = "HS256"

# In-memory revoked token set (and can be backed by Redis if enabled)
_REVOKED_TOKENS: set[str] = set()

def create_access_token(
    subject: Union[str, Any],
    role: str = "USER",
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    jti = secrets.token_urlsafe(16)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "jti": jti,
        "iat": datetime.now(timezone.utc)
    }
    if extra_claims:
        to_encode.update(extra_claims)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and jti in _REVOKED_TOKENS:
            return None
        return payload
    except Exception:
        return None

def is_token_revoked(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        return bool(jti and jti in _REVOKED_TOKENS)
    except Exception:
        return False

def revoke_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            _REVOKED_TOKENS.add(jti)
            return True
    except Exception:
        pass
    return False

# Safe native bcrypt password operations
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

# TOTP / MFA Utilities
def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, user_email: str, issuer_name: str = "PayPath") -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name=issuer_name)

def verify_totp_code(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    # Validates with 1 time step window for clock skew tolerance
    return totp.verify(code.strip(), valid_window=1)

# Secure Password Reset Tokens
def generate_password_reset_token() -> tuple[str, str, datetime]:
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return raw_token, hashed_token, expires_at

def hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
