import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.policy import MerchantPolicy, PolicyChunk
from app.models.transaction import Transaction, TransactionEvent, Subscription
from app.models.reclaim import ReclaimCase, Evidence
from app.core.security import get_password_hash
from app.rag.chunker import policy_chunker
from app.rag.vector_store import vector_store
from app.core.observability import logger

DEMO_USER_ID = "usr_demo_shopper_01"
NOVA_MERCHANT_ID = "mch_nova_electronics"

async def seed_demo_data(db: AsyncSession) -> None:
    """Seeds the database with realistic sandbox data for the demo narrative."""
    # Check if any user already exists
    user_stmt = select(User)
    existing_user = (await db.execute(user_stmt)).scalars().first()
    if existing_user:
        logger.info("Demo data already seeded in database. Skipping startup seeding.")
        return

    logger.info("Seeding demo merchants, users, policies, and transactions...")

    # 1. Demo User
    demo_user = User(
        id=DEMO_USER_ID,
        email="demo@paypath.finance",
        full_name="Alex Chen",
        hashed_password=get_password_hash("paypath123!"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(demo_user)
    await db.flush()

    # 2. Merchants
    merchants_data = [
        {"id": NOVA_MERCHANT_ID, "name": "Nova Electronics", "slug": "nova-electronics", "email": "support@novaelectronics.demo"},
        {"id": "mch_urban_fit", "name": "UrbanFit", "slug": "urban-fit", "email": "help@urbanfit.demo"},
        {"id": "mch_travel_hub", "name": "TravelHub", "slug": "travel-hub", "email": "concierge@travelhub.demo"},
        {"id": "mch_media_nest", "name": "MediaNest", "slug": "media-nest", "email": "billing@medianest.demo"}
    ]
    for m in merchants_data:
        merchant = Merchant(
            id=m["id"],
            name=m["name"],
            slug=m["slug"],
            support_email=m["email"],
            is_verified=True
        )
        db.add(merchant)
    await db.flush()

    # 3. Policies & RAG Chunks
    nova_policy_text = """
# Nova Electronics Customer Assurance Policy

## 1. Return Window & Eligibility
Customers may return items within 30 days of confirmed delivery for standard returns. All returned goods must include original packaging and accessories.

## 2. Damaged Goods & Transit Defects
If an item arrives damaged, defective, or structurally compromised during transit, customers are entitled to:
- A replacement shipped immediately with expedited delivery, OR
- A partial refund up to 75% if the customer opts to retain the product for cosmetic defects.
Photographic proof of the transit damage is required for claims.

## 3. Restocking Fees
Standard returns for change-of-mind are subject to a 10% restocking fee. Defective or damaged items are exempt from any restocking fees.

## 4. Refund Settlement
Approved refunds are processed via PayPal back to the original funding source within 1 business day.
"""
    nova_policy = MerchantPolicy(
        id="pol_nova_assurance",
        merchant_id=NOVA_MERCHANT_ID,
        title="Nova Electronics Customer Assurance Policy v2.1",
        policy_type="REFUND",
        raw_content=nova_policy_text,
        status="PUBLISHED",
        version=2,
        rules_json={"return_window_days": 30, "partial_refund_max_pct": 75, "damage_eligible": True}
    )
    db.add(nova_policy)

    # Index into RAG vector store and database
    chunks = policy_chunker.chunk_document(nova_policy_text, merchant_id=NOVA_MERCHANT_ID, title=nova_policy.title)
    for c in chunks:
        vector_store.add_chunk(c)
        chunk_obj = PolicyChunk(
            policy_id=nova_policy.id,
            merchant_id=NOVA_MERCHANT_ID,
            section_title=c.get("title", "Policy Section"),
            content=c["content"],
            embedding=vector_store.generate_embedding(c["content"])
        )
        db.add(chunk_obj)

    # 4. Historical Transactions
    now = datetime.now(timezone.utc)
    t1 = Transaction(
        id="tx_nova_anc_hero",
        user_id=DEMO_USER_ID,
        merchant_id=NOVA_MERCHANT_ID,
        merchant_name="Nova Electronics",
        paypal_order_id="5O190127TN364715T",
        paypal_capture_id="3C498126Y8012941P",
        amount=89.00,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.08,
        risk_level="LOW",
        ai_summary="NovaSound ANC Pro Wireless Headphones purchased for travel under policy spend guard.",
        item_description="NovaSound ANC Pro Wireless Headphones",
        created_at=now - timedelta(days=14)
    )
    db.add(t1)

    # Timeline event for t1
    e1 = TransactionEvent(
        transaction_id=t1.id,
        event_type="PAYPAL_PAYMENT_CAPTURED",
        actor="PAYPAL",
        description="PayPal payment captured successfully. Verified by PayPal read-back audit.",
        created_at=now - timedelta(days=14)
    )
    db.add(e1)

    # Duplicate payment scenario
    t2 = Transaction(
        id="tx_media_nest_01",
        user_id=DEMO_USER_ID,
        merchant_id="mch_media_nest",
        merchant_name="MediaNest",
        paypal_order_id="6M829104PA102948X",
        paypal_capture_id="8C194820LK294819M",
        amount=14.99,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.15,
        risk_level="LOW",
        ai_summary="Monthly digital streaming subscription payment.",
        item_description="MediaNest Premium Streaming (Monthly)",
        created_at=now - timedelta(days=3)
    )
    t3 = Transaction(
        id="tx_media_nest_dup",
        user_id=DEMO_USER_ID,
        merchant_id="mch_media_nest",
        merchant_name="MediaNest",
        paypal_order_id="7M829104PA102949Y",
        paypal_capture_id="9C194820LK294820N",
        amount=14.99,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.78,
        risk_level="HIGH",
        ai_summary="Potential duplicate charge detected: Identical amount ($14.99) charged within 5 minutes.",
        item_description="MediaNest Premium Streaming (Monthly)",
        created_at=now - timedelta(days=3, minutes=4)
    )
    db.add(t2)
    db.add(t3)

    # Subscriptions
    sub = Subscription(
        id="sub_media_nest",
        user_id=DEMO_USER_ID,
        merchant_name="MediaNest",
        amount=14.99,
        currency="USD",
        billing_interval="MONTHLY",
        last_payment_date=(now - timedelta(days=3)).strftime("%Y-%m-%d"),
        next_expected_date=(now + timedelta(days=27)).strftime("%Y-%m-%d"),
        status="ACTIVE"
    )
    db.add(sub)

    await db.commit()
    logger.info("Database successfully seeded with demo entities.")

