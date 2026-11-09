import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import (
    User, UserRole, Merchant, MerchantPolicy, PolicyChunk,
    Transaction, TransactionEvent, ReclaimCase, Evidence,
    Subscription, AuditLog, Notification
)
from app.rag.vector_store import vector_store
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(User).where(User.email == "demo@paypath.ai"))
        if res.scalars().first():
            print("Database already contains demo user. Skipping seed.")
            return

        print("Seeding PostgreSQL 16 with production-grade demo data...")

        # 1. Demo User
        demo_user = User(
            email="demo@paypath.ai",
            hashed_password=get_password_hash("PayPath2026!Secure"),
            full_name="Alex Mercer",
            role=UserRole.PLATFORM_ADMIN,
            is_active=True,
            mfa_enabled=False
        )
        session.add(demo_user)
        await session.flush()

        # 2. Demo Merchant
        merchant = Merchant(
            name="Apex Gear Co.",
            slug="apex-gear",
            paypal_merchant_id="APEX_MERCHANT_01",
            support_email="support@apexgear.io",
            is_verified=True
        )
        session.add(merchant)
        await session.flush()

        # 3. Merchant Policy
        policy = MerchantPolicy(
            merchant_id=merchant.id,
            title="Apex Standard Return & Refund Policy 2026",
            policy_type="REFUND",
            version=1,
            status="PUBLISHED",
            raw_content="""
Apex Gear Co. Standard Customer Policy:
1. Returns are accepted within 30 days of delivery.
2. Defective or damaged items received upon delivery are eligible for an immediate partial refund up to 75% or full replacement without restocking fees.
3. For minor transit cosmetic damage, a standard resolution credit of $65.00 applies to items under $100.
4. Maximum autonomous refund limit is $250.00. Amounts above $250.00 require human escalation.
5. Subscriptions can be cancelled at any time before the billing cycle renews.
            """.strip(),
            rules_json=[
                {"condition": "days_since_delivery <= 30", "action": "ALLOW_RETURN"},
                {"condition": "issue == 'DAMAGED_ITEM' and item_price < 100", "action": "ALLOW_PARTIAL_REFUND", "amount": 65.00},
                {"condition": "refund_amount > 250", "action": "REQUIRE_HUMAN_APPROVAL"}
            ]
        )
        session.add(policy)
        await session.flush()

        # 4. Policy Chunks with embeddings
        chunks_data = [
            ("Return Window", "Returns are accepted within 30 days of delivery for all consumer electronics."),
            ("Damage Allowance", "Defective or damaged items received upon delivery are eligible for an immediate partial refund up to 75% or full replacement without restocking fees."),
            ("Cosmetic Damage Credit", "For minor transit cosmetic damage, a standard resolution credit of $65.00 applies to items under $100 upon photographic verification."),
            ("Autonomous Limits", "Maximum autonomous refund limit is $250.00. Amounts above $250.00 require human escalation."),
            ("Cancellation Policy", "Subscriptions can be cancelled at any time before the billing cycle renews.")
        ]
        for title, text in chunks_data:
            emb = vector_store.generate_embedding(text)
            chunk = PolicyChunk(
                policy_id=policy.id,
                merchant_id=merchant.id,
                section_title=title,
                content=text,
                embedding=emb,
                chunk_metadata={"section": title, "merchant_slug": "apex-gear"}
            )
            session.add(chunk)

        # 5. Transactions
        t1 = Transaction(
            user_id=demo_user.id,
            merchant_id=merchant.id,
            merchant_name="Apex Gear Co.",
            paypal_order_id="ORD-8921-APEX",
            paypal_capture_id="CAP-8921-APEX-01",
            amount=89.00,
            currency="USD",
            status="CAPTURED",
            verification_status="VERIFIED",
            risk_score=12.5,
            risk_level="LOW",
            item_description="Apex Wireless ANC Headphones (Matte Black)",
            ai_summary="Standard verified purchase. Carrier tracking confirms delivered 48 hours ago."
        )
        session.add(t1)

        t2 = Transaction(
            user_id=demo_user.id,
            merchant_id=merchant.id,
            merchant_name="CloudSync Pro",
            paypal_order_id="ORD-4412-CLOUD",
            paypal_capture_id="CAP-4412-CLOUD-01",
            amount=29.99,
            currency="USD",
            status="CAPTURED",
            verification_status="VERIFIED",
            risk_score=5.0,
            risk_level="LOW",
            item_description="CloudSync Pro 100GB Monthly Subscription",
            ai_summary="Recurring monthly cloud storage tier."
        )
        session.add(t2)

        t3 = Transaction(
            user_id=demo_user.id,
            merchant_id=merchant.id,
            merchant_name="Apex Gear Co.",
            paypal_order_id="ORD-1092-SUPPLY",
            paypal_capture_id="CAP-1092-SUPPLY-01",
            amount=145.50,
            currency="USD",
            status="CAPTURED",
            verification_status="VERIFIED",
            risk_score=8.0,
            risk_level="LOW",
            item_description="ErgoDesk Pro Monitor Stand (Dual Arm)",
            ai_summary="Hardware accessory delivered without reported anomalies."
        )
        session.add(t3)

        t4 = Transaction(
            user_id=demo_user.id,
            merchant_id=merchant.id,
            merchant_name="Apex Gear Co.",
            paypal_order_id="ORD-3319-DUP",
            paypal_capture_id="CAP-3319-DUP-01",
            amount=89.00,
            currency="USD",
            status="CREATED",
            verification_status="PENDING",
            risk_score=88.5,
            risk_level="HIGH",
            item_description="Apex Wireless ANC Headphones (Duplicate Order Detected)",
            ai_summary="Suspicious transaction: identical SKU and amount ordered within 48 hours."
        )
        session.add(t4)
        await session.flush()

        # 6. Reclaim Case on t1 (Damaged Headphones)
        rc = ReclaimCase(
            transaction_id=t1.id,
            user_id=demo_user.id,
            issue_type="DAMAGED_ITEM",
            description="Right ear cup arrived with deep scuff and cracked casing from transit.",
            status="AI_RECOMMENDED",
            proposed_resolution="PARTIAL_REFUND",
            recommended_amount=65.00,
            confidence_score=0.96,
            ai_reasoning="Customer provided photographic evidence of cosmetic transit damage. Apex Policy Rule 3 authorizes a fixed $65.00 settlement credit for items under $100 without requiring physical return.",
            policy_citation={"rule": "Rule 3: Transit Cosmetic Damage Credit", "limit": 65.00},
            approval_status="PENDING"
        )
        session.add(rc)
        await session.flush()

        ev = Evidence(
            reclaim_case_id=rc.id,
            file_name="damaged_headphone_earcup.jpg",
            file_type="image/jpeg",
            file_url="/uploads/damaged_headphone_earcup.jpg",
            evidence_type="PHOTO_DAMAGE",
            analysis_summary="Visual analysis detects 3.2cm hairline surface crack across polycarbonate hinge assembly. Matches customer report.",
            confidence_score=0.96
        )
        session.add(ev)

        # 7. Subscriptions for recurring intelligence
        sub = Subscription(
            user_id=demo_user.id,
            merchant_name="CloudSync Pro",
            amount=29.99,
            currency="USD",
            billing_interval="MONTHLY",
            last_payment_date="2026-10-15",
            next_expected_date="2026-11-15",
            status="ACTIVE"
        )
        session.add(sub)

        # 8. Notifications
        n1 = Notification(
            user_id=demo_user.id,
            title="RECLAIM Settlement Ready for Approval",
            message="A $65.00 partial refund resolution is awaiting your authorization for 'Apex Wireless ANC Headphones'.",
            notification_type="PAYMENT_APPROVAL_REQUIRED",
            action_url="/reclaim",
            is_read=False
        )
        n2 = Notification(
            user_id=demo_user.id,
            title="Payment Guard Anomaly Alert",
            message="Potential duplicate transaction ($89.00) flagged on Apex Gear Co.",
            notification_type="ANOMALY_DETECTED",
            action_url="/guard",
            is_read=False
        )
        session.add(n1)
        session.add(n2)

        # 9. Audit Log
        audit = AuditLog(
            action="SYSTEM_INIT_SEED",
            actor_type="USER",
            actor_id=demo_user.id,
            resource_type="DATABASE",
            resource_id="paypath",
            details={"database": "paypath", "seeded_tables": 14},
            ip_address="127.0.0.1"
        )
        session.add(audit)

        await session.commit()
        print("PostgreSQL 16 seeded successfully with production demo data!")

if __name__ == "__main__":
    asyncio.run(seed())
