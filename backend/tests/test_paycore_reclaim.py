import pytest
from app.core.database import AsyncSessionLocal, init_db
from app.services.seed_service import seed_demo_data, DEMO_USER_ID, NOVA_MERCHANT_ID
from app.paycore.service import PayCoreService
from app.agents.orchestrator import agent_orchestrator
from app.models.transaction import Transaction
from sqlalchemy import select

@pytest.mark.asyncio
async def test_complete_paycore_and_reclaim_lifecycle():
    # 1. Initialize tables and seed
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)

    async with AsyncSessionLocal() as session:
        service = PayCoreService(session)

        # 2. Create PayPal Order
        order_res = await service.create_order(
            user_id=DEMO_USER_ID,
            amount=89.00,
            currency="USD",
            merchant_name="Nova Electronics",
            merchant_id=NOVA_MERCHANT_ID,
            item_description="NovaSound ANC Pro Headphones"
        )
        assert order_res["status"] == "CREATED"
        assert order_res["amount"] == 89.00
        order_id = order_res["order_id"]

        # 3. Capture Order
        capture_res = await service.capture_order(order_id=order_id, user_id=DEMO_USER_ID)
        assert capture_res["status"] == "CAPTURED"
        assert capture_res["verification_status"] == "VERIFIED"
        tx_id = capture_res["transaction_id"]

        # 4. Agentic RECLAIM Workflow
        workflow = await agent_orchestrator.execute_reclaim_workflow(
            transaction_amount=89.00,
            merchant_name="Nova Electronics",
            issue_type="DAMAGED_ITEM",
            user_description="Plastic headband cracked on delivery.",
            evidence_file_name="cracked_headband.jpg"
        )
        assert workflow["resolution"]["proposed_resolution"] == "PARTIAL_REFUND"
        assert workflow["resolution"]["recommended_amount"] == 65.00
        assert workflow["policy_check"]["decision"] == "ALLOW"

        # 5. Execute Approved Refund
        refund_res = await service.execute_refund(
            transaction_id=tx_id,
            amount=65.00,
            currency="USD",
            reason="Customer reported damaged item approved by user",
            idempotency_key=f"test_refund_{tx_id}"
        )
        assert refund_res["status"] == "COMPLETED"
        assert refund_res["is_verified"] is True
        assert refund_res["verification_status"] == "VERIFIED"

        # 6. Verify Transaction state in DB
        stmt = select(Transaction).where(Transaction.id == tx_id)
        tx = (await session.execute(stmt)).scalar_one()
        assert tx.status == "PARTIALLY_REFUNDED"
        assert tx.verification_status == "VERIFIED"

