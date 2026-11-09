import pytest
from app.agents.intent_agent import intent_agent
from app.agents.shopping_agent import shopping_agent
from app.agents.evidence_agent import evidence_agent
from app.agents.resolution_agent import resolution_agent

@pytest.mark.asyncio
async def test_intent_agent_extraction():
    prompt = "I need headphones under $100 for travel. Don't purchase anything unless I approve it."
    extracted = await intent_agent.parse_intent(prompt)
    assert extracted["category"] == "headphones"
    assert extracted["purpose"] == "travel"
    assert extracted["budget"] == 100.0
    assert extracted["approval_required"] is True
    assert extracted["autonomy"] == "RESTRICTED"

@pytest.mark.asyncio
async def test_shopping_agent_recommendation():
    recs = await shopping_agent.search_and_recommend(category="headphones", budget=100.0, purpose="travel")
    assert len(recs) > 0
    top_pick = recs[0]
    assert top_pick["price"] <= 100.0
    assert top_pick["matches_budget"] is True

@pytest.mark.asyncio
async def test_evidence_agent_analysis():
    result = await evidence_agent.analyze_evidence(
        file_name="broken_headband.jpg",
        issue_type="DAMAGED_ITEM",
        user_description="The plastic headband snapped during shipping."
    )
    assert result["evidence_classification"] == "STRUCTURAL_DAMAGE_CONFIRMED"
    assert result["confidence_score"] >= 0.90
    assert result["verified_evidence"] is True

@pytest.mark.asyncio
async def test_resolution_agent_proposal():
    policy_citation = {
        "policy_title": "Nova Electronics Return Policy",
        "section": "Damaged Goods & Transit Defects"
    }
    proposal = await resolution_agent.propose_resolution(
        transaction_amount=89.00,
        issue_type="DAMAGED_ITEM",
        evidence_summary="Cracked plastic headband",
        policy_citation=policy_citation
    )
    assert proposal["proposed_resolution"] == "PARTIAL_REFUND"
    assert proposal["recommended_amount"] == 65.00
    assert proposal["confidence_score"] >= 0.90
    assert proposal["requires_approval"] is True
