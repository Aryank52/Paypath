import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.reclaim import ReclaimCase, Evidence
from app.schemas.reclaim import (
    CreateReclaimCaseRequest,
    ReclaimCaseResponse,
    ReclaimEvaluationResponse,
    EvidenceAnalysisResult
)
from app.agents.orchestrator import agent_orchestrator
from app.paycore.service import PayCoreService
from app.api.deps import get_current_user

router = APIRouter(prefix="/reclaim", tags=["RECLAIM Resolution Engine"])

@router.post("/cases", response_model=ReclaimCaseResponse)
async def create_case(
    payload: CreateReclaimCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Transaction).where(
        Transaction.id == payload.transaction_id,
        Transaction.user_id == current_user.id
    )
    tx = (await db.execute(stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    case = ReclaimCase(
        transaction_id=tx.id,
        user_id=current_user.id,
        issue_type=payload.issue_type,
        description=payload.description,
        status="EVIDENCE_REQUIRED",
        approval_status="PENDING"
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)

    return ReclaimCaseResponse(
        id=case.id,
        transaction_id=case.transaction_id,
        user_id=case.user_id,
        issue_type=case.issue_type,
        description=case.description,
        status=case.status,
        approval_status=case.approval_status,
        created_at=case.created_at
    )

@router.post("/cases/{case_id}/evidence", response_model=EvidenceAnalysisResult)
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(ReclaimCase).where(
        ReclaimCase.id == case_id,
        ReclaimCase.user_id == current_user.id
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Dispute case not found.")

    # Read uploaded file metadata
    file_name = file.filename or "evidence_photo.jpg"
    file_url = f"/uploads/{case_id}/{file_name}"

    # Analyze via Evidence Agent
    from app.agents.evidence_agent import evidence_agent
    analysis = await evidence_agent.analyze_evidence(
        file_name=file_name,
        issue_type=case.issue_type,
        user_description=case.description
    )

    evidence = Evidence(
        reclaim_case_id=case.id,
        file_name=file_name,
        file_type=file.content_type or "image/jpeg",
        file_url=file_url,
        evidence_type="PHOTO_DAMAGE",
        analysis_summary=analysis["analysis_summary"],
        confidence_score=analysis["confidence_score"]
    )
    db.add(evidence)
    case.status = "UNDER_REVIEW"
    await db.commit()
    await db.refresh(evidence)

    return EvidenceAnalysisResult(
        evidence_id=evidence.id,
        file_name=evidence.file_name,
        file_url=evidence.file_url,
        evidence_type=evidence.evidence_type,
        confidence_score=float(evidence.confidence_score),
        analysis_summary=evidence.analysis_summary
    )

@router.post("/cases/{case_id}/evaluate", response_model=ReclaimEvaluationResponse)
async def evaluate_reclaim_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(ReclaimCase).where(
        ReclaimCase.id == case_id,
        ReclaimCase.user_id == current_user.id
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    tx_stmt = select(Transaction).where(Transaction.id == case.transaction_id)
    tx = (await db.execute(tx_stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Associated transaction not found.")

    # Run multi-agent RECLAIM workflow
    workflow = await agent_orchestrator.execute_reclaim_workflow(
        transaction_amount=float(tx.amount),
        merchant_name=tx.merchant_name,
        issue_type=case.issue_type,
        user_description=case.description,
        evidence_file_name="headband_damage.jpg"
    )

    res = workflow["resolution"]
    case.proposed_resolution = res["proposed_resolution"]
    case.recommended_amount = res["recommended_amount"]
    case.confidence_score = res["confidence_score"]
    case.ai_reasoning = res["ai_reasoning"]
    case.policy_citation = res["policy_citation"]
    case.status = "AWAITING_APPROVAL"
    await db.commit()

    return ReclaimEvaluationResponse(
        case_id=case.id,
        proposed_resolution=res["proposed_resolution"],
        recommended_amount=float(res["recommended_amount"]),
        confidence_score=float(res["confidence_score"]),
        ai_reasoning=res["ai_reasoning"],
        policy_citation=res["policy_citation"],
        requires_approval=True,
        status=case.status
    )

@router.post("/cases/{case_id}/approve")
async def approve_and_execute_refund(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Human-in-the-loop approval gate:
    User authorizes the proposed resolution.
    PayPath dispatches refund via PayCore to PayPal Sandbox and independently verifies settlement.
    """
    stmt = select(ReclaimCase).where(
        ReclaimCase.id == case_id,
        ReclaimCase.user_id == current_user.id
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not case.recommended_amount or case.recommended_amount <= 0:
        raise HTTPException(status_code=400, detail="No approved refund amount on this case.")

    # Execute PayPal Refund via PayCore
    paycore_service = PayCoreService(db)
    refund_result = await paycore_service.execute_refund(
        transaction_id=case.transaction_id,
        amount=float(case.recommended_amount),
        currency="USD",
        reason=f"RECLAIM Case {case.id} Approved: {case.issue_type}",
        idempotency_key=f"reclaim_refund_{case.id}",
        actor_id=current_user.id
    )

    # Mark case resolved
    case.status = "RESOLVED"
    case.approval_status = "USER_APPROVED"
    await db.commit()
    await db.refresh(case)

    return {
        "case_id": case.id,
        "status": "RESOLVED",
        "resolution": case.proposed_resolution,
        "amount_refunded": float(case.recommended_amount),
        "paypal_refund_id": refund_result["refund_id"],
        "is_verified": refund_result["is_verified"],
        "verification_status": refund_result["verification_status"],
        "badge": "Verified by PayPal"
    }

@router.get("/cases/{case_id}", response_model=ReclaimCaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(ReclaimCase).where(
        ReclaimCase.id == case_id,
        ReclaimCase.user_id == current_user.id
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    ev_stmt = select(Evidence).where(Evidence.reclaim_case_id == case.id)
    ev_result = await db.execute(ev_stmt)
    evidence_list = ev_result.scalars().all()

    return ReclaimCaseResponse(
        id=case.id,
        transaction_id=case.transaction_id,
        user_id=case.user_id,
        issue_type=case.issue_type,
        description=case.description,
        status=case.status,
        proposed_resolution=case.proposed_resolution,
        recommended_amount=float(case.recommended_amount) if case.recommended_amount else None,
        confidence_score=float(case.confidence_score) if case.confidence_score else None,
        ai_reasoning=case.ai_reasoning,
        policy_citation=case.policy_citation,
        approval_status=case.approval_status,
        created_at=case.created_at,
        evidence_items=[
            EvidenceAnalysisResult(
                evidence_id=e.id,
                file_name=e.file_name,
                file_url=e.file_url,
                evidence_type=e.evidence_type,
                confidence_score=float(e.confidence_score) if e.confidence_score else 0.9,
                analysis_summary=e.analysis_summary or ""
            ) for e in evidence_list
        ]
    )
