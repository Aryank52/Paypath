"""
Machine Learning Subsystem API Routes.
Provides:
- Model Registry inspection (registered versions and performance metrics)
- Transaction Explainability (feature contributions, anomaly breakdown)
- Ad-hoc Risk Scoring & Policy Recommendations
- Feature Definitions metadata

SAFETY DIRECTIVE:
All outputs from this router are advisory signals.
Final authorization or refund actions are governed strictly by the Policy Engine and Human Approval.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ml import MLModelVersion, MLPrediction
from app.models.transaction import Transaction
from app.ml.features import FEATURE_NAMES
from app.ml.inference import get_ml_service

router = APIRouter(prefix="/ml", tags=["Machine Learning Intelligence"])

class PredictRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant_name: str = Field(..., description="Target merchant name")
    item_description: Optional[str] = Field(default="", description="Product or purchase description")
    user_id: Optional[str] = Field(default=None, description="User identifier for velocity calculation")
    is_subscription: Optional[bool] = Field(default=False, description="Whether transaction is a recurring billing")

@router.get("/models")
async def list_model_versions(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieves all registered ML model versions from PostgreSQL registry."""
    result = await db.execute(
        select(MLModelVersion).order_by(MLModelVersion.created_at.desc())
    )
    records = result.scalars().all()
    models = []
    for r in records:
        models.append({
            "id": r.id,
            "model_name": r.model_name,
            "algorithm": r.algorithm,
            "version": r.version,
            "feature_version": r.feature_version,
            "training_dataset": r.training_dataset,
            "trained_at": r.trained_at.isoformat() if r.trained_at else None,
            "status": r.status,
            "metrics": r.metrics,
            "artifact_path": r.artifact_path,
        })
    return {
        "count": len(models),
        "models": models,
    }

@router.get("/features")
async def get_feature_definitions() -> Dict[str, Any]:
    """Returns the deterministic 12-feature schema used by PayPath ML models."""
    definitions = {
        "amount": "Numerical transaction amount in USD.",
        "velocity_24h": "Count of transactions initiated by this user within prior 24 hours.",
        "velocity_7d": "Count of transactions initiated by this user within prior 7 days.",
        "amount_velocity_24h": "Aggregate USD amount spent by this user in prior 24 hours.",
        "hour_of_day": "Transaction initiation hour (0-23 UTC).",
        "day_of_week": "Transaction day of week (0=Monday, 6=Sunday).",
        "is_weekend": "Binary flag (1 if Saturday or Sunday, else 0).",
        "user_avg_amount_ratio": "Ratio of current amount to user historical average purchase size.",
        "merchant_risk_historical": "Historical merchant chargeback and dispute frequency prior.",
        "is_subscription": "Binary flag (1 for recurring/interval subscriptions, else 0).",
        "high_risk_mcc": "Binary flag (1 for luxury electronics, rapid crypto, or wire keywords).",
        "duplicate_window_match": "Binary flag (1 if identical amount charged to same merchant within 1 hour).",
    }
    return {
        "feature_count": len(FEATURE_NAMES),
        "features": FEATURE_NAMES,
        "definitions": definitions,
        "leakage_prevention": "No post-settlement or dispute outcome fields are included in model features.",
    }

@router.get("/explain/{transaction_id}")
async def explain_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Computes real-time explainability breakdown and feature contributions for a given transaction.
    """
    tx = await db.get(Transaction, transaction_id)
    if not tx or (tx.user_id != current_user.id and current_user.role != UserRole.PLATFORM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )

    # Fetch recent user transactions for velocity context
    history_res = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == tx.user_id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
    )
    history = history_res.scalars().all()

    ml_service = get_ml_service()
    tx_dict = {
        "id": tx.id,
        "user_id": tx.user_id,
        "merchant_name": tx.merchant_name,
        "amount": float(tx.amount),
        "currency": tx.currency,
        "status": tx.status,
        "verification_status": tx.verification_status,
        "risk_score": float(tx.risk_score),
        "risk_level": tx.risk_level,
        "item_description": tx.item_description or "",
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
        "meta_info": tx.meta_info or {},
    }

    hist_dicts = [
        {
            "id": h.id,
            "user_id": h.user_id,
            "merchant_name": h.merchant_name,
            "amount": float(h.amount),
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in history
        if h.id != tx.id
    ]

    prediction = ml_service.predict(tx_dict, hist_dicts)
    return {
        "transaction_id": tx.id,
        "amount": float(tx.amount),
        "merchant_name": tx.merchant_name,
        "status": tx.status,
        "ml_explanation": prediction,
    }

@router.post("/predict")
async def predict_risk(payload: PredictRequest) -> Dict[str, Any]:
    """
    On-demand risk and anomaly evaluation for simulated or pre-authorization transactions.
    """
    ml_service = get_ml_service()
    tx_data = {
        "amount": payload.amount,
        "merchant_name": payload.merchant_name,
        "item_description": payload.item_description or "",
        "user_id": payload.user_id or "anonymous",
        "meta_info": {"is_subscription": payload.is_subscription},
    }
    prediction = ml_service.predict(tx_data)
    return prediction

