"""
Full System End-to-End Integration Tests for PayPath.
Verifies the complete transaction lifecycle:
Understand -> Decide -> Act -> Verify.

Scenario 1: Agentic Commerce & Payment Guard Purchase Workflow
Scenario 2: RECLAIM Autonomous Dispute, Policy RAG, Human Approval & Refund Settlement
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.seed_service import seed_demo_data
from app.ml.train import train_and_register_models

@pytest.mark.asyncio
async def test_end_to_end_agentic_commerce_lifecycle():
    """
    Test complete commerce journey:
    Intent Parsing -> Product Selection -> Payment Guard Evaluation ->
    Order Creation -> Order Capture -> Dual-Phase Read-Back Verification -> ML Scoring.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 0: Auth Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "demo@paypath.finance", "password": "paypath123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: User Intent Parsing
        intent_res = await client.post("/api/v1/intent/parse", json={
            "prompt": "Find me premium noise cancelling headphones for flights under $100"
        })
        assert intent_res.status_code == 200
        intent = intent_res.json()
        assert intent["category"] in ["headphones", "Audio", "audio"]
        assert intent["budget"] == 100.0

        # Step 2: Product Search (category=headphones)
        search_res = await client.get("/api/v1/shop/search?category=headphones&budget=100")
        assert search_res.status_code == 200
        products = search_res.json()
        assert len(products) > 0
        product = products[0]

        # Step 3: Payment Guard Policy Check
        guard_res = await client.post("/api/v1/guard/evaluate", json={
            "amount": float(product["price"]),
            "merchant_name": "Nova Electronics",
            "category": "headphones"
        })
        assert guard_res.status_code == 200
        guard = guard_res.json()
        assert guard["is_allowed"] is True
        assert guard["decision"] == "ALLOW"

        # Step 4: PayCore Order Creation
        order_res = await client.post("/api/v1/paycore/orders/create", json={
            "amount": float(product["price"]),
            "currency": "USD",
            "merchant_name": "Nova Electronics",
            "item_description": product["title"]
        }, headers=headers)
        assert order_res.status_code == 200
        order = order_res.json()
        assert order["status"] == "CREATED"
        order_id = order["order_id"]

        # Step 5: PayCore Order Capture
        capture_res = await client.post("/api/v1/paycore/orders/capture", json={
            "order_id": order_id
        }, headers=headers)
        assert capture_res.status_code == 200
        capture = capture_res.json()
        assert capture["status"] in ["COMPLETED", "CAPTURED"]
        assert capture["verification_status"] == "VERIFIED"
        # Step 6: Verify Transaction in DB
        tx_list_res = await client.get("/api/v1/transactions", headers=headers)
        assert tx_list_res.status_code == 200
        tx_list = tx_list_res.json()
        matching = [t for t in tx_list if t.get("paypal_order_id") == order_id]
        assert len(matching) > 0
        tx = matching[0]
        tx_id = tx["id"]
        assert tx["verification_status"] == "VERIFIED"
        assert tx["amount"] == float(product["price"])

        # Step 7: Explainability check on new transaction
        ml_res = await client.get(f"/api/v1/ml/explain/{tx_id}", headers=headers)
        assert ml_res.status_code == 200
        explanation = ml_res.json()["ml_explanation"]
        assert "risk_score" in explanation
        assert explanation["policy_recommendation"] in ["ALLOW", "REVIEW", "BLOCK"]

@pytest.mark.asyncio
async def test_end_to_end_reclaim_dispute_and_refund_lifecycle():
    """
    Test complete RECLAIM dispute lifecycle:
    Dispute Submission -> RAG Policy Analysis -> Multi-Agent Consensus ->
    Human Approval -> Refund Mutation -> Read-Back Verification.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 0: Auth Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "demo@paypath.finance", "password": "paypath123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Create Dispute Case
        case_res = await client.post("/api/v1/reclaim/cases", json={
            "transaction_id": "tx_nova_anc_hero",
            "issue_type": "DAMAGED_ITEM",
            "description": "Right ear cup cracked upon delivery impact."
        }, headers=headers)
        assert case_res.status_code == 200
        case = case_res.json()
        case_id = case["id"]

        # Step 2: Autonomous Case Evaluation & RAG Policy Lookup
        eval_res = await client.post(f"/api/v1/reclaim/cases/{case_id}/evaluate", headers=headers)
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert eval_data["proposed_resolution"] in ["PARTIAL_REFUND", "REPLACEMENT"]
        assert eval_data["confidence_score"] >= 0.85
        assert eval_data["requires_approval"] is True
        assert eval_data["status"] == "AWAITING_APPROVAL"

        # Step 3: Human User Approval
        approve_res = await client.post(f"/api/v1/reclaim/cases/{case_id}/approve", headers=headers)
        assert approve_res.status_code == 200
        approved = approve_res.json()
        assert approved["status"] == "RESOLVED"
        assert approved["badge"] == "Verified by PayPal"
        assert approved["is_verified"] is True

        # Step 4: Verify Case State Persisted
        final_case = await client.get(f"/api/v1/reclaim/cases/{case_id}", headers=headers)
        assert final_case.status_code == 200
        assert final_case.json()["status"] in ["RESOLVED", "APPROVED"]
