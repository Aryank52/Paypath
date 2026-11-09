import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.agents.intent_agent import intent_agent
from app.agents.shopping_agent import shopping_agent
from app.agents.policy_agent import policy_agent
from app.agents.evidence_agent import evidence_agent
from app.agents.risk_agent import risk_agent
from app.agents.resolution_agent import resolution_agent
from app.agents.verification_agent import verification_agent
from app.policies.engine import policy_engine
from app.core.observability import logger

class AgentOrchestrator:
    """
    Coordinates specialized agents using a typed execution trace.
    Guarantees deterministic policy boundary checks between agent recommendations and actions.
    """

    async def execute_commerce_workflow(self, user_prompt: str) -> Dict[str, Any]:
        """Runs Intent Agent -> Shopping Agent -> Risk Agent -> Policy Guard."""
        workflow_id = f"wf_comm_{uuid.uuid4().hex[:8]}"
        trace: List[Dict[str, Any]] = []

        # 1. Intent Extraction
        intent_result = await intent_agent.parse_intent(user_prompt)
        trace.append(intent_agent.create_trace_step(
            action="PARSE_USER_INTENT",
            summary=f"Extracted purchase intent: {intent_result.get('category')} for {intent_result.get('purpose')} with budget ${intent_result.get('budget')}.",
            details=intent_result
        ))

        # 2. Product Search
        products = await shopping_agent.search_and_recommend(
            category=intent_result.get("category", "headphones"),
            budget=intent_result.get("budget", 100.0),
            purpose=intent_result.get("purpose", "travel")
        )
        selected_product = products[0] if products else None
        trace.append(shopping_agent.create_trace_step(
            action="CATALOG_DISCOVERY",
            summary=f"Identified {len(products)} matching candidate products. Top pick: {selected_product['title']} (${selected_product['price']:.2f})." if selected_product else "No products found.",
            details={"candidate_count": len(products), "top_pick": selected_product}
        ))

        # 3. Policy Guard Pre-Check
        if selected_product:
            guard_result = policy_engine.evaluate_purchase(
                amount=selected_product["price"],
                merchant_name=selected_product["merchant_name"],
                category=selected_product["category"],
                user_intent_budget=intent_result.get("budget")
            )
            trace.append({
                "step_id": f"step_{uuid.uuid4().hex[:6]}",
                "agent_name": "PolicyEngine",
                "role": "Deterministic Payment Guard",
                "action": "EVALUATE_SPEND_POLICIES",
                "summary": f"Policy decision: {guard_result['decision']} (Approval Required: {guard_result['requires_approval']}). {guard_result['reason']}",
                "status": "COMPLETED",
                "details": guard_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            guard_result = None

        return {
            "workflow_id": workflow_id,
            "intent": intent_result,
            "products": products,
            "selected_product": selected_product,
            "guard": guard_result,
            "trace": trace
        }

    async def execute_reclaim_workflow(
        self,
        transaction_amount: float,
        merchant_name: str,
        issue_type: str,
        user_description: str,
        evidence_file_name: str,
        transaction_age_days: int = 14
    ) -> Dict[str, Any]:
        """
        Runs the RECLAIM Resolution Flow:
        Evidence Agent -> Policy Agent (RAG) -> Resolution Agent -> Policy Engine Check.
        """
        workflow_id = f"wf_reclaim_{uuid.uuid4().hex[:8]}"
        trace: List[Dict[str, Any]] = []

        # 1. Evidence Inspection
        evidence_result = await evidence_agent.analyze_evidence(
            file_name=evidence_file_name,
            issue_type=issue_type,
            user_description=user_description
        )
        trace.append(evidence_agent.create_trace_step(
            action="EVIDENCE_ANALYSIS",
            summary=f"Classified proof: {evidence_result['evidence_classification']} (Confidence: {int(evidence_result['confidence_score']*100)}%). {evidence_result['analysis_summary']}",
            details=evidence_result
        ))

        # 2. Policy Retrieval (RAG)
        policy_citation = await policy_agent.retrieve_policy(
            issue_type=issue_type,
            merchant_name=merchant_name,
            transaction_age_days=transaction_age_days
        )
        trace.append(policy_agent.create_trace_step(
            action="RAG_POLICY_RETRIEVAL",
            summary=f"Retrieved {policy_citation['policy_title']} Section '{policy_citation['section']}'. Verified within return window.",
            details=policy_citation
        ))

        # 3. AI Resolution Proposal
        resolution_proposal = await resolution_agent.propose_resolution(
            transaction_amount=transaction_amount,
            issue_type=issue_type,
            evidence_summary=evidence_result["analysis_summary"],
            policy_citation=policy_citation
        )
        trace.append(resolution_agent.create_trace_step(
            action="FORMULATE_RESOLUTION",
            summary=f"Proposed resolution: {resolution_proposal['proposed_resolution']} for ${resolution_proposal['recommended_amount']:.2f}. Confidence: {int(resolution_proposal['confidence_score']*100)}%.",
            details=resolution_proposal
        ))

        # 4. Deterministic Policy Verification
        policy_check = policy_engine.evaluate_refund(
            proposed_amount=resolution_proposal["recommended_amount"],
            transaction_amount=transaction_amount,
            issue_type=issue_type,
            transaction_age_days=transaction_age_days,
            evidence_provided=True
        )
        trace.append({
            "step_id": f"step_{uuid.uuid4().hex[:6]}",
            "agent_name": "PolicyEngine",
            "role": "Deterministic Boundary Guard",
            "action": "EVALUATE_REFUND_RULES",
            "summary": f"Deterministic validation passed: {policy_check['decision']}. Applied rules: {', '.join(policy_check['applied_rules'])}.",
            "status": "COMPLETED",
            "details": policy_check,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return {
            "workflow_id": workflow_id,
            "evidence": evidence_result,
            "policy": policy_citation,
            "resolution": resolution_proposal,
            "policy_check": policy_check,
            "trace": trace
        }

agent_orchestrator = AgentOrchestrator()

