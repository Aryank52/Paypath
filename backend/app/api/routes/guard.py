from fastapi import APIRouter
from app.schemas.guard import GuardEvaluationRequest, GuardEvaluationResponse
from app.policies.engine import policy_engine

router = APIRouter(prefix="/guard", tags=["Payment Guard"])

@router.post("/evaluate", response_model=GuardEvaluationResponse)
async def evaluate_transaction_guard(payload: GuardEvaluationRequest):
    result = policy_engine.evaluate_purchase(
        amount=payload.amount,
        merchant_name=payload.merchant_name,
        category=payload.category or "general"
    )
    return GuardEvaluationResponse(
        decision=result["decision"],
        is_allowed=result["is_allowed"],
        requires_approval=result["requires_approval"],
        reason=result["reason"],
        risk_score=result["risk_score"],
        applied_rules=result["applied_rules"],
        max_budget=result.get("max_budget"),
        requested_amount=result["requested_amount"]
    )

@router.get("/rules")
async def get_active_guard_rules():
    return {
        "max_amount_per_transaction": policy_engine.spend_rules.max_amount_per_transaction,
        "auto_approval_threshold": policy_engine.spend_rules.auto_approval_threshold,
        "restricted_categories": policy_engine.spend_rules.restricted_categories,
        "flagged_merchants": policy_engine.spend_rules.flagged_merchants
    }
