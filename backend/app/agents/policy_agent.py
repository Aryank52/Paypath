from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.rag.retriever import policy_retriever

class PolicyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PolicyAgent", role="Merchant Policy Retrieval & Evidence Citation")

    async def retrieve_policy(
        self,
        issue_type: str,
        merchant_name: str = "Nova Electronics",
        merchant_id: Optional[str] = None,
        transaction_age_days: int = 14
    ) -> Dict[str, Any]:
        citation = policy_retriever.retrieve_policy_for_issue(
            issue_type=issue_type,
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            transaction_age_days=transaction_age_days
        )
        return citation

policy_agent = PolicyAgent()
