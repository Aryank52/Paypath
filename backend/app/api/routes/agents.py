from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.orchestrator import agent_orchestrator

router = APIRouter(prefix="/agents", tags=["Agent Orchestrator"])

class AgentCommerceRunRequest(BaseModel):
    prompt: str

class AgentReclaimRunRequest(BaseModel):
    transaction_amount: float = 89.00
    merchant_name: str = "Nova Electronics"
    issue_type: str = "DAMAGED_ITEM"
    user_description: str = "Headphones arrived with cracked headband."
    evidence_file_name: str = "broken_headband.jpg"
    transaction_age_days: int = 14

@router.post("/run-commerce")
async def run_commerce_agents(payload: AgentCommerceRunRequest):
    result = await agent_orchestrator.execute_commerce_workflow(payload.prompt)
    return result

@router.post("/run-reclaim")
async def run_reclaim_agents(payload: AgentReclaimRunRequest):
    result = await agent_orchestrator.execute_reclaim_workflow(
        transaction_amount=payload.transaction_amount,
        merchant_name=payload.merchant_name,
        issue_type=payload.issue_type,
        user_description=payload.user_description,
        evidence_file_name=payload.evidence_file_name,
        transaction_age_days=payload.transaction_age_days
    )
    return result

