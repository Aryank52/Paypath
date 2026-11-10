import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.policy import MerchantPolicy
from app.models.transaction import Transaction
from app.rag.chunker import policy_chunker
from app.rag.vector_store import vector_store
from app.policies.engine import policy_engine
from app.core.observability import logger

router = APIRouter(prefix="/merchants", tags=["Multi-Merchant Portal & Policy Simulation"])

class CreateMerchantRequest(BaseModel):
    name: str = Field(..., examples=["EcoTech Living"])
    slug: str = Field(..., examples=["ecotech-living"])
    support_email: Optional[str] = "support@ecotech.demo"
    paypal_merchant_id: Optional[str] = "MCH-ECOTECH-SANDBOX"

class MerchantPolicyUploadRequest(BaseModel):
    title: str = Field(..., examples=["EcoTech 45-Day Warranty & Defect Policy"])
    policy_type: str = Field(default="REFUND")
    content: str = Field(..., description="Markdown or text policy clauses")
    rules: Optional[Dict[str, Any]] = None

class PolicySimulationRequest(BaseModel):
    transaction_amount: float = Field(default=120.0)
    issue_type: str = Field(default="DAMAGED_ITEM")
    transaction_age_days: int = Field(default=18)
    evidence_provided: bool = Field(default=True)
    custom_rules: Optional[Dict[str, Any]] = None

@router.get("")
async def list_merchants(db: AsyncSession = Depends(get_db)):
    stmt = select(Merchant).order_by(Merchant.name.asc())
    result = await db.execute(stmt)
    merchants = result.scalars().all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "slug": m.slug,
            "support_email": m.support_email,
            "is_verified": m.is_verified,
            "created_at": m.created_at
        } for m in merchants
    ]

from app.models.user import User, UserRole
from app.api.deps import get_current_user, require_role

@router.post("")
async def onboard_merchant(
    payload: CreateMerchantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT_ADMIN, UserRole.PLATFORM_ADMIN))
):
    stmt = select(Merchant).where(Merchant.slug == payload.slug)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant slug already registered.")

    merchant = Merchant(
        name=payload.name,
        slug=payload.slug,
        support_email=payload.support_email,
        paypal_merchant_id=payload.paypal_merchant_id,
        is_verified=True
    )
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return {
        "id": merchant.id,
        "name": merchant.name,
        "slug": merchant.slug,
        "status": "ACTIVE",
        "message": "Merchant onboarded successfully into isolated tenant namespace."
    }

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found.")

    # Policies
    pol_stmt = select(MerchantPolicy).where(MerchantPolicy.merchant_id == m.id)
    policies = (await db.execute(pol_stmt)).scalars().all()

    return {
        "id": m.id,
        "name": m.name,
        "slug": m.slug,
        "support_email": m.support_email,
        "policies": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "version": p.version,
                "rules": p.rules_json
            } for p in policies
        ]
    }

@router.post("/{merchant_id}/policies")
async def upload_merchant_policy(
    merchant_id: str,
    payload: MerchantPolicyUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT_ADMIN, UserRole.PLATFORM_ADMIN))
):
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found.")

    policy = MerchantPolicy(
        merchant_id=m.id,
        title=payload.title,
        policy_type=payload.policy_type,
        raw_content=payload.content,
        status="DRAFT", # Draft until published
        version=1,
        rules_json=payload.rules or {"return_window_days": 30, "partial_refund_max_pct": 75}
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    from app.models.policy import PolicyChunk

    # Chunk and index into isolated tenant vector space (both in-memory and PostgreSQL)
    chunks = policy_chunker.chunk_document(payload.content, merchant_id=m.id, title=payload.title)
    for c in chunks:
        vector_store.add_chunk(c)
        chunk_obj = PolicyChunk(
            policy_id=policy.id,
            merchant_id=m.id,
            section_title=c.get("title", payload.title),
            content=c["content"],
            embedding=vector_store.generate_embedding(c["content"])
        )
        db.add(chunk_obj)
    await db.commit()

    return {
        "id": policy.id,
        "title": policy.title,
        "status": policy.status,
        "chunks_indexed": len(chunks),
        "message": "Policy ingested and chunked as DRAFT. Publish to activate for live transactions."
    }

@router.post("/{merchant_id}/policies/{policy_id}/publish")
async def publish_policy(
    merchant_id: str,
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT_ADMIN, UserRole.PLATFORM_ADMIN))
):
    stmt = select(MerchantPolicy).where(
        MerchantPolicy.id == policy_id,
        MerchantPolicy.merchant_id == merchant_id
    )
    policy = (await db.execute(stmt)).scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    policy.status = "PUBLISHED"
    await db.commit()
    await db.refresh(policy)
    return {
        "id": policy.id,
        "status": "PUBLISHED",
        "message": f"Policy '{policy.title}' is now active for live resolution decisions."
    }

@router.post("/{merchant_id}/simulate-policy")
async def simulate_policy_decision(
    merchant_id: str,
    payload: PolicySimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Policy Simulation Engine:
    Transaction + Evidence + Policy = Predicted Outcome
    """
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    m = (await db.execute(stmt)).scalar_one_or_none()
    merchant_name = m.name if m else "Custom Merchant"

    proposed_amount = round(payload.transaction_amount * 0.75, 2)
    evaluation = policy_engine.evaluate_refund(
        proposed_amount=proposed_amount,
        transaction_amount=payload.transaction_amount,
        issue_type=payload.issue_type,
        transaction_age_days=payload.transaction_age_days,
        evidence_provided=payload.evidence_provided
    )

    return {
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "simulated_input": {
            "transaction_amount": payload.transaction_amount,
            "proposed_refund": proposed_amount,
            "issue_type": payload.issue_type,
            "transaction_age_days": payload.transaction_age_days,
            "evidence_provided": payload.evidence_provided
        },
        "predicted_outcome": {
            "decision": evaluation["decision"],
            "is_allowed": evaluation["is_allowed"],
            "requires_human_approval": evaluation["requires_approval"],
            "reason": evaluation["reason"],
            "applied_rules": evaluation["applied_rules"]
        }
    }

