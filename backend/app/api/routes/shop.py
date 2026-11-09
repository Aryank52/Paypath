from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.agents.shopping_agent import shopping_agent
from app.policies.engine import policy_engine

router = APIRouter(prefix="/shop", tags=["Shopping"])

@router.get("/search")
async def search_products(
    category: str = Query("headphones"),
    budget: Optional[float] = Query(100.0),
    purpose: str = Query("travel")
):
    recommendations = await shopping_agent.search_and_recommend(
        category=category,
        budget=budget,
        purpose=purpose
    )
    return recommendations

@router.post("/propose-purchase")
async def propose_purchase(
    product_id: str,
    amount: float,
    merchant_name: str,
    category: str = "headphones",
    user_budget: Optional[float] = None
):
    guard_eval = policy_engine.evaluate_purchase(
        amount=amount,
        merchant_name=merchant_name,
        category=category,
        user_intent_budget=user_budget
    )
    return {
        "product_id": product_id,
        "amount": amount,
        "merchant_name": merchant_name,
        "guard_evaluation": guard_eval,
        "requires_human_approval": guard_eval["requires_approval"],
        "is_approved": guard_eval["decision"] == "ALLOW"
    }
