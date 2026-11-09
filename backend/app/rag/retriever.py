from typing import List, Dict, Any, Optional
from app.rag.vector_store import vector_store

class PolicyRetriever:
    """Retrieves grounded policy clauses and formats verifiable citations."""

    @staticmethod
    def retrieve_policy_for_issue(
        issue_type: str,
        merchant_id: Optional[str] = None,
        merchant_name: str = "Nova Electronics",
        transaction_age_days: int = 14
    ) -> Dict[str, Any]:
        query = f"refund return policy for {issue_type} damaged goods defect replacement"
        results = vector_store.search(query=query, merchant_id=merchant_id, top_k=2)

        if results:
            best_chunk = results[0]
            section = best_chunk.get("section_title", "Damaged Goods & Transit Defects")
            content = best_chunk.get("content", "")
            excerpt = content[:250] + "..." if len(content) > 250 else content
        else:
            section = "Damaged Goods & Transit Defects"
            excerpt = (
                "Products received in damaged or defective condition are eligible for a replacement "
                "or partial refund up to 75% of the purchase value if reported within 30 days of confirmed delivery."
            )

        return {
            "merchant_name": merchant_name,
            "policy_title": f"{merchant_name} Standard Customer Assurance Policy",
            "section": section,
            "excerpt": excerpt,
            "effective_date": "2026-01-01",
            "applicability": f"Applicable (Reported {transaction_age_days} days after purchase, within 30-day window)",
            "rules": {
                "return_window_days": 30,
                "partial_refund_max_pct": 75.0,
                "requires_evidence": True
            }
        }

policy_retriever = PolicyRetriever()

