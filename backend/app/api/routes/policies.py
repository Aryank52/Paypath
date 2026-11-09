from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.policy import MerchantPolicy
from app.schemas.policy import PolicyUploadRequest, PolicyQueryRequest, PolicyResponse
from app.rag.chunker import policy_chunker
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/policies", tags=["Policies & RAG"])

@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    merchant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MerchantPolicy)
    if merchant_id:
        stmt = stmt.where(MerchantPolicy.merchant_id == merchant_id)
    result = await db.execute(stmt)
    policies = result.scalars().all()
    return list(policies)

@router.post("/upload", response_model=PolicyResponse)
async def upload_policy(
    payload: PolicyUploadRequest,
    db: AsyncSession = Depends(get_db)
):
    policy = MerchantPolicy(
        merchant_id=payload.merchant_id,
        title=payload.title,
        policy_type=payload.policy_type,
        raw_content=payload.content,
        rules_json=payload.rules or {"return_window_days": 30, "partial_refund_max_pct": 75}
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    # Chunk and index into vector store
    chunks = policy_chunker.chunk_document(payload.content, merchant_id=payload.merchant_id, title=payload.title)
    for c in chunks:
        vector_store.add_chunk(c)

    return policy

@router.post("/query")
async def query_policies(payload: PolicyQueryRequest):
    results = vector_store.search(
        query=payload.query,
        merchant_id=payload.merchant_id,
        top_k=payload.top_k
    )
    return results

