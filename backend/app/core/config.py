from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    APP_NAME: str = "PayPath"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "paypath-dev-secret-key-326ebfdb-5cc7-4b18-a149"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database (PostgreSQL is authoritative; SQLite restricted to test environments)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/paypath",
        description="Async SQLAlchemy database URL. PostgreSQL is the authoritative system of record."
    )
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Supabase Storage (Evidence & File Persistence)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "paypath-evidence"
    
    # CORS Configuration
    ALLOWED_ORIGINS: Optional[str] = None
    
    # PayPal Sandbox
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_BASE_URL: str = "https://api-m.sandbox.paypal.com"
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_WEBHOOK_ID: Optional[str] = None
    
    # AI Engine
    GEMINI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"
    
    # Feature Flags
    ENABLE_VOICE: bool = True
    ENABLE_SHOPPING: bool = True
    ENABLE_CHANNEL3: bool = False
    ENABLE_AGENTIC_PURCHASE: bool = True
    ENABLE_RECOVERY: bool = True
    ENABLE_RECLAIM: bool = True
    ENABLE_MULTI_MERCHANT: bool = True
    ENABLE_EMAIL: bool = False
    ENABLE_ZAPIER: bool = False
    ENABLE_ELASTIC: bool = False
    ENABLE_BRYNTUM: bool = False
    ENABLE_KERNEL: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

