import pytest
from app.policies.engine import DeterministicPolicyEngine
from app.policies.rules import SpendPolicyRule, RefundPolicyRule

def test_purchase_allowed_within_budget():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_purchase(
        amount=89.00,
        merchant_name="Nova Electronics",
        category="headphones",
        user_intent_budget=100.00
    )
    assert result["is_allowed"] is True
    assert result["decision"] == "ALLOW"
    assert result["requires_approval"] is True # > $50 threshold

def test_purchase_blocked_when_exceeding_user_intent_budget():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_purchase(
        amount=120.00,
        merchant_name="Nova Electronics",
        category="headphones",
        user_intent_budget=100.00
    )
    assert result["is_allowed"] is False
    assert result["decision"] == "BLOCK"
    assert "USER_INTENT_BUDGET_EXCEEDED" in result["applied_rules"]

def test_purchase_blocked_for_restricted_category():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_purchase(
        amount=25.00,
        merchant_name="Some Vendor",
        category="gambling"
    )
    assert result["is_allowed"] is False
    assert result["decision"] == "BLOCK"
    assert "RESTRICTED_CATEGORY_RULE" in result["applied_rules"]

def test_refund_allowed_within_window_with_damage():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_refund(
        proposed_amount=65.00,
        transaction_amount=89.00,
        issue_type="DAMAGED_ITEM",
        transaction_age_days=14,
        evidence_provided=True
    )
    assert result["is_allowed"] is True
    assert result["decision"] == "ALLOW"
    assert result["requires_approval"] is True

def test_refund_blocked_exceeding_total():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_refund(
        proposed_amount=100.00,
        transaction_amount=89.00,
        issue_type="DAMAGED_ITEM"
    )
    assert result["is_allowed"] is False
    assert result["decision"] == "BLOCK"
    assert "REFUND_EXCEEDS_TRANSACTION_AMOUNT" in result["applied_rules"]

def test_refund_escalated_beyond_window():
    engine = DeterministicPolicyEngine()
    result = engine.evaluate_refund(
        proposed_amount=65.00,
        transaction_amount=89.00,
        issue_type="DAMAGED_ITEM",
        transaction_age_days=45 # > 30 days
    )
    assert result["decision"] == "ESCALATE"
    assert result["is_allowed"] is False

