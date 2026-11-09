from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.models.intent import PurchaseIntent
from app.schemas.intent import IntentParseRequest, IntentResponse
from app.agents.intent_agent import intent_agent
from app.api.deps import get_current_user

router = APIRouter(prefix="/intent", tags=["Intent"])

@router.post("/parse", response_model=IntentResponse)
async def parse_and_store_intent(
    payload: IntentParseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    extracted = await intent_agent.parse_intent(payload.prompt)

    # Persist structured intent in DB
    intent = PurchaseIntent(
        user_id=current_user.id,
        raw_prompt=payload.prompt,
        category=extracted.get("category"),
        purpose=extracted.get("purpose"),
        budget_amount=extracted.get("budget"),
        currency=extracted.get("currency", "USD"),
        approval_required=extracted.get("approval_required", True),
        autonomy_level=extracted.get("autonomy", "RESTRICTED"),
        status="ACTIVE"
    )
    db.add(intent)
    await db.commit()
    await db.refresh(intent)

    return IntentResponse(
        id=intent.id,
        category=intent.category,
        purpose=intent.purpose,
        budget=float(intent.budget_amount) if intent.budget_amount else None,
        currency=intent.currency,
        approval_required=intent.approval_required,
        autonomy=intent.autonomy_level,
        raw_prompt=intent.raw_prompt,
        created_at=intent.created_at
    )
