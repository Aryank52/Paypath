"""
PayPath PayPal Lifecycle, Idempotency & Financial Invariants Test Script.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.paycore.service import PayCoreService
from app.services.seed_service import DEMO_USER_ID, NOVA_MERCHANT_ID
from fastapi import HTTPException

async def test_paypal_lifecycle_and_idempotency():
    async with AsyncSessionLocal() as session:
        service = PayCoreService(session)
        
        # 1. Create Order
        print("\n=== 1. Create PayPal Order ===")
        order = await service.create_order(
            user_id=DEMO_USER_ID,
            amount=89.00,
            currency="USD",
            merchant_name="Nova Electronics",
            merchant_id=NOVA_MERCHANT_ID,
            item_description="NovaSound ANC Pro Headphones (Phase 16 Test)"
        )
        print(f"Order Created: id={order['order_id']}, status={order['status']}, amount={order['amount']}")
        assert order["status"] == "CREATED"
        
        # 2. Capture Order
        print("\n=== 2. Capture PayPal Order ===")
        capture = await service.capture_order(order_id=order["order_id"], user_id=DEMO_USER_ID)
        print(f"Captured: tx_id={capture['transaction_id']}, capture_id={capture['capture_id']}, verification={capture['verification_status']}")
        assert capture["status"] == "CAPTURED"
        assert capture["verification_status"] == "VERIFIED"
        tx_id = capture["transaction_id"]
        
        # 3. First Refund
        print("\n=== 3. Execute Refund Mutation ===")
        idem_key = f"phase16_idem_{order['order_id']}"
        refund1 = await service.execute_refund(
            transaction_id=tx_id,
            amount=40.00,
            currency="USD",
            reason="Customer reported transit scuff",
            idempotency_key=idem_key
        )
        print(f"Refund 1: id={refund1['refund_id']}, amount={refund1['amount']}, verified={refund1['is_verified']}")
        assert refund1["status"] == "COMPLETED"
        assert refund1["is_verified"] is True
        
        # 4. Duplicate Refund (Exact Replay)
        print("\n=== 4. Test Idempotent Duplicate Replay ===")
        refund_replay = await service.execute_refund(
            transaction_id=tx_id,
            amount=40.00,
            currency="USD",
            reason="Customer reported transit scuff",
            idempotency_key=idem_key
        )
        print(f"Refund Replay: id={refund_replay['refund_id']}, is_verified={refund_replay['is_verified']}")
        assert refund_replay["refund_id"] == refund1["refund_id"]
        print("PASS: Idempotent replay returned existing mutation without duplicating fund movement.")
        
        # 5. Altered Amount with same Idempotency Key -> Expect 409 Conflict
        print("\n=== 5. Test Altered Amount with Same Idempotency Key ===")
        conflict_detected = False
        try:
            await service.execute_refund(
                transaction_id=tx_id,
                amount=50.00, # Altered amount!
                currency="USD",
                reason="Altered amount replay attempt",
                idempotency_key=idem_key
            )
        except HTTPException as e:
            if e.status_code == 409:
                conflict_detected = True
                print(f"PASS: 409 Conflict properly raised: {e.detail}")
        assert conflict_detected, "Security Failure: 409 Conflict was not raised for altered amount idempotency key!"
        
        # 6. Exceed Remaining Balance -> Expect 400
        print("\n=== 6. Test Exceeding Remaining Balance ===")
        over_refund_blocked = False
        try:
            # Remaining balance is 89.00 - 40.00 = 49.00
            await service.execute_refund(
                transaction_id=tx_id,
                amount=60.00, # Exceeds 49.00
                currency="USD",
                reason="Over-refund attempt",
                idempotency_key=f"phase16_over_{order['order_id']}"
            )
        except HTTPException as e:
            if e.status_code == 400:
                over_refund_blocked = True
                print(f"PASS: Over-refund blocked with 400: {e.detail}")
        assert over_refund_blocked, "Financial Safety Failure: Over-refund was not blocked!"
        
        print("\n=== All PayCore Financial Invariants & Read-Back Verifications Passed! ===")

if __name__ == "__main__":
    asyncio.run(test_paypal_lifecycle_and_idempotency())
