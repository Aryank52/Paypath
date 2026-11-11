"""
PayPath Comprehensive Database Seed Service.
Populates PostgreSQL 16 with a realistic, multi-merchant financial ecosystem:
- 5 Users (Shoppers, Merchant Admin, Platform Admin)
- 5 Merchants (Electronics, Fitness, Travel, Home Goods, Media)
- 20 Products in catalog
- 5 Structured Merchant Policies with RAG chunks and vector embeddings
- 65+ Realistic Transactions with timeline events (normal, high risk, duplicate, subscription)
- 4 RECLAIM Cases with Evidence analysis
- 4 Active Subscriptions
- 8 System & Security Notifications
- ML Predictions generated from active models
- Agent Runs & Tool Calls demonstrating multi-agent workflows

IDEMPOTENCY:
Supports safe idempotent re-runs, targeted verification, and forced reset.
"""

from datetime import datetime, timezone, timedelta
import random
from typing import Any, Dict, List, Optional
from sqlalchemy import select, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.core.observability import logger
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.policy import MerchantPolicy, PolicyChunk
from app.models.product import Product
from app.models.transaction import Transaction, TransactionEvent, Subscription
from app.models.reclaim import ReclaimCase, Evidence
from app.models.notification import Notification
from app.models.ml import MLModelVersion, MLPrediction
from app.models.agent import AgentRun, AgentToolCall
from app.models.payment_action import PaymentAction, PaymentVerification
from app.models.intent import PurchaseIntent
from app.models.audit import AuditLog
from app.models.webhook import WebhookEvent
from app.rag.chunker import policy_chunker
from app.rag.vector_store import vector_store
from app.ml.inference import get_ml_service
from app.ml.train import train_and_register_models

# Fixed canonical IDs for consistent cross-references
USER_ALEX_ID = "usr_demo_shopper_01"
USER_SARAH_ID = "usr_merchant_admin_02"
USER_MARCUS_ID = "usr_platform_admin_03"
USER_ELENA_ID = "usr_shopper_elena_04"
USER_DEVIN_ID = "usr_shopper_devin_05"

DEMO_USER_ID = USER_ALEX_ID
NOVA_MERCHANT_ID = "mch_nova_electronics"

MCH_NOVA_ID = NOVA_MERCHANT_ID
MCH_URBAN_ID = "mch_urban_fit"
MCH_TRAVEL_ID = "mch_travel_hub"
MCH_HOME_ID = "mch_home_craft"
MCH_MEDIA_ID = "mch_media_nest"

TX_HERO_ANC_ID = "tx_nova_anc_hero"
TX_MEDIA_01_ID = "tx_media_nest_01"
TX_MEDIA_DUP_ID = "tx_media_nest_dup"
TX_TRAVEL_EXP_ID = "tx_travel_expired"
TX_HOME_SET_ID = "tx_home_dinner_set"

RECLAIM_HERO_CASE_ID = "rc_nova_damage_hero"
RECLAIM_DUP_CASE_ID = "rc_media_duplicate"
RECLAIM_TRAVEL_CASE_ID = "rc_travel_expired"
RECLAIM_HOME_CASE_ID = "rc_home_missing_item"

async def reset_demo_data(db: AsyncSession) -> None:
    """Safely wipes all demo transactional and catalog data using TRUNCATE CASCADE."""
    logger.info("Executing safe database reset for seed re-initialization...")
    from sqlalchemy import text
    truncate_query = text("""
        TRUNCATE TABLE 
            payment_verifications, 
            payment_actions, 
            purchase_intents, 
            audit_logs, 
            agent_tool_calls, 
            agent_runs, 
            ml_predictions, 
            notifications, 
            evidence, 
            reclaim_cases, 
            subscriptions, 
            transaction_events, 
            transactions, 
            products, 
            policy_chunks, 
            merchant_policies, 
            merchants, 
            users 
        RESTART IDENTITY CASCADE;
    """)
    await db.execute(truncate_query)
    await db.commit()
    logger.info("Database tables cleanly truncated.")

async def seed_demo_data(db: AsyncSession, force_reset: bool = False) -> Dict[str, Any]:
    """
    Idempotently seeds all 14 PayPath entities into PostgreSQL 16.
    """
    if force_reset:
        await reset_demo_data(db)

    # Check if primary demo user already exists
    existing = await db.scalar(
        select(func.count(User.id)).where(
            or_(User.id == USER_ALEX_ID, User.email == "demo@paypath.finance")
        )
    )
    if existing and not force_reset:
        logger.info("Demo data already seeded. Checking supplementary entities...")
        actions_count = await db.scalar(select(func.count(PaymentAction.id)))
        if not actions_count:
            logger.info("Populating supplementary lineage records (actions, verifications, intents, audit)...")
            await _seed_supplementary_records(db, datetime.now(timezone.utc))
            await db.commit()
        return await verify_demo_data(db)

    logger.info("Starting comprehensive seed sequence across 14 tables...")
    now = datetime.now(timezone.utc)

    # ----------------------------------------------------
    # 1. USERS (5 users: 3 shoppers, 1 merchant admin, 1 platform admin)
    # ----------------------------------------------------
    hashed_pwd = get_password_hash("paypath123!")
    users_data = [
        User(
            id=USER_ALEX_ID,
            email="demo@paypath.finance",
            full_name="Alex Chen",
            hashed_password=hashed_pwd,
            role=UserRole.USER,
            is_active=True,
            mfa_enabled=False,
        ),
        User(
            id=USER_SARAH_ID,
            email="sarah.jenkins@paypath.finance",
            full_name="Sarah Jenkins",
            hashed_password=hashed_pwd,
            role=UserRole.MERCHANT_ADMIN,
            is_active=True,
            mfa_enabled=True,
        ),
        User(
            id=USER_MARCUS_ID,
            email="marcus.vance@paypath.finance",
            full_name="Marcus Vance",
            hashed_password=hashed_pwd,
            role=UserRole.PLATFORM_ADMIN,
            is_active=True,
            mfa_enabled=True,
        ),
        User(
            id=USER_ELENA_ID,
            email="elena.rostova@paypath.finance",
            full_name="Elena Rostova",
            hashed_password=hashed_pwd,
            role=UserRole.USER,
            is_active=True,
            mfa_enabled=False,
        ),
        User(
            id=USER_DEVIN_ID,
            email="devin.cole@paypath.finance",
            full_name="Devin Cole",
            hashed_password=hashed_pwd,
            role=UserRole.USER,
            is_active=True,
            mfa_enabled=False,
        ),
    ]
    db.add_all(users_data)
    await db.flush()

    # ----------------------------------------------------
    # 2. MERCHANTS (5 diverse merchants)
    # ----------------------------------------------------
    merchants_data = [
        Merchant(
            id=MCH_NOVA_ID,
            name="Nova Electronics",
            slug="nova-electronics",
            paypal_merchant_id="MCH_NOVA_01",
            support_email="support@novaelectronics.demo",
            is_verified=True,
        ),
        Merchant(
            id=MCH_URBAN_ID,
            name="UrbanFit",
            slug="urban-fit",
            paypal_merchant_id="MCH_URBAN_02",
            support_email="help@urbanfit.demo",
            is_verified=True,
        ),
        Merchant(
            id=MCH_TRAVEL_ID,
            name="TravelHub",
            slug="travel-hub",
            paypal_merchant_id="MCH_TRAVEL_03",
            support_email="concierge@travelhub.demo",
            is_verified=True,
        ),
        Merchant(
            id=MCH_HOME_ID,
            name="HomeCraft",
            slug="home-craft",
            paypal_merchant_id="MCH_HOME_04",
            support_email="artisan@homecraft.demo",
            is_verified=True,
        ),
        Merchant(
            id=MCH_MEDIA_ID,
            name="MediaNest",
            slug="media-nest",
            paypal_merchant_id="MCH_MEDIA_05",
            support_email="billing@medianest.demo",
            is_verified=True,
        ),
    ]
    db.add_all(merchants_data)
    await db.flush()

    # ----------------------------------------------------
    # 3. PRODUCTS CATALOG (4 products per merchant = 20 products)
    # ----------------------------------------------------
    products_data = [
        # Nova Electronics
        Product(
            id="prod_nova_01",
            merchant_id=MCH_NOVA_ID,
            name="NovaSound ANC Pro Wireless Headphones",
            slug="novasound-anc-pro",
            category="Audio",
            description="Active noise-canceling over-ear headphones with 40-hour battery life and studio clarity.",
            price=89.00,
            currency="USD",
            in_stock=True,
            rating=4.8,
            image_url="/products/nova_anc.jpg",
            meta_info={"warranty_months": 24, "sku": "NE-ANC-PRO"},
        ),
        Product(
            id="prod_nova_02",
            merchant_id=MCH_NOVA_ID,
            name="Quantum 4K Ultra Gaming Monitor 27\"",
            slug="quantum-4k-monitor",
            category="Displays",
            description="165Hz IPS 1ms HDR400 gaming monitor with FreeSync and USB-C power delivery.",
            price=349.99,
            currency="USD",
            in_stock=True,
            rating=4.7,
            image_url="/products/quantum_monitor.jpg",
            meta_info={"warranty_months": 36, "sku": "NE-MON-4K"},
        ),
        Product(
            id="prod_nova_03",
            merchant_id=MCH_NOVA_ID,
            name="NovaCharge 100W GaN Fast Charger",
            slug="novacharge-100w",
            category="Accessories",
            description="Compact 3-port USB-C fast charger compatible with laptops, phones, and tablets.",
            price=39.99,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/gan_charger.jpg",
            meta_info={"warranty_months": 12, "sku": "NE-CHG-100"},
        ),
        Product(
            id="prod_nova_04",
            merchant_id=MCH_NOVA_ID,
            name="NovaPad Air Mechanical Keyboard",
            slug="novapad-air-keyboard",
            category="Peripherals",
            description="Hot-swappable tactile mechanical keyboard with RGB backlighting and wireless connectivity.",
            price=119.50,
            currency="USD",
            in_stock=True,
            rating=4.6,
            image_url="/products/novapad_keyboard.jpg",
            meta_info={"warranty_months": 24, "sku": "NE-KB-AIR"},
        ),
        # UrbanFit
        Product(
            id="prod_urban_01",
            merchant_id=MCH_URBAN_ID,
            name="UrbanFlex Seamless Yoga Mat Pro",
            slug="urbanflex-yoga-mat",
            category="Fitness",
            description="Eco-friendly natural tree rubber yoga mat with laser-etched alignment guides.",
            price=48.00,
            currency="USD",
            in_stock=True,
            rating=4.8,
            image_url="/products/urban_mat.jpg",
            meta_info={"thickness_mm": 5, "sku": "UF-MAT-PRO"},
        ),
        Product(
            id="prod_urban_02",
            merchant_id=MCH_URBAN_ID,
            name="SpeedStride Carbon Running Shoes",
            slug="speedstride-shoes",
            category="Footwear",
            description="Ultra-lightweight marathon running shoes with full-length carbon fiber propulsion plate.",
            price=145.00,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/speedstride.jpg",
            meta_info={"weight_grams": 195, "sku": "UF-RUN-STRIDE"},
        ),
        Product(
            id="prod_urban_03",
            merchant_id=MCH_URBAN_ID,
            name="TitanGrip Resistance Band Set",
            slug="titangrip-bands",
            category="Fitness",
            description="Set of 5 premium stackable resistance bands with handles, door anchor, and ankle straps.",
            price=24.99,
            currency="USD",
            in_stock=True,
            rating=4.7,
            image_url="/products/titangrip.jpg",
            meta_info={"max_resistance_lbs": 150, "sku": "UF-BAND-SET"},
        ),
        Product(
            id="prod_urban_04",
            merchant_id=MCH_URBAN_ID,
            name="HydraPulse Insulated 32oz Bottle",
            slug="hydrapulse-bottle",
            category="Accessories",
            description="Double-wall vacuum insulated stainless steel water bottle keeping drinks cold for 24 hours.",
            price=32.00,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/hydrapulse.jpg",
            meta_info={"capacity_oz": 32, "sku": "UF-BTL-32"},
        ),
        # TravelHub
        Product(
            id="prod_travel_01",
            merchant_id=MCH_TRAVEL_ID,
            name="Express Flight Booking (SFO -> JFK)",
            slug="flight-sfo-jfk",
            category="Flights",
            description="Non-stop transcontinental economy fare with 1 personal item and standard carry-on included.",
            price=385.00,
            currency="USD",
            in_stock=True,
            rating=4.5,
            image_url="/products/flight_ticket.jpg",
            meta_info={"carrier": "TransSky", "refundable_hours": 24},
        ),
        Product(
            id="prod_travel_02",
            merchant_id=MCH_TRAVEL_ID,
            name="Boutique Hotel Stay 2 Nights",
            slug="boutique-hotel-2n",
            category="Lodging",
            description="Deluxe King suite in downtown metro area with complimentary breakfast and high-speed Wi-Fi.",
            price=240.00,
            currency="USD",
            in_stock=True,
            rating=4.6,
            image_url="/products/hotel_stay.jpg",
            meta_info={"check_in": "15:00", "cancellation_notice_hours": 48},
        ),
        Product(
            id="prod_travel_03",
            merchant_id=MCH_TRAVEL_ID,
            name="Global Travel Guard Insurance",
            slug="travel-insurance",
            category="Insurance",
            description="Comprehensive trip cancellation, emergency medical, and lost luggage protection.",
            price=45.00,
            currency="USD",
            in_stock=True,
            rating=4.8,
            image_url="/products/travel_guard.jpg",
            meta_info={"coverage_max": 25000},
        ),
        Product(
            id="prod_travel_04",
            merchant_id=MCH_TRAVEL_ID,
            name="Airport VIP Lounge One-Day Pass",
            slug="vip-lounge-pass",
            category="Services",
            description="All-inclusive lounge access with hot buffet, premium beverages, shower suites, and quiet pods.",
            price=55.00,
            currency="USD",
            in_stock=True,
            rating=4.4,
            image_url="/products/vip_lounge.jpg",
            meta_info={"valid_hours": 24},
        ),
        # HomeCraft
        Product(
            id="prod_home_01",
            merchant_id=MCH_HOME_ID,
            name="Handmade Stoneware Dinner Set (16-Piece)",
            slug="stoneware-dinner-set",
            category="Dining",
            description="Artisan-thrown stoneware dining collection including dinner plates, salad plates, bowls, and mugs.",
            price=128.00,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/stoneware_set.jpg",
            meta_info={"material": "Glazed Stoneware", "dishwasher_safe": True},
        ),
        Product(
            id="prod_home_02",
            merchant_id=MCH_HOME_ID,
            name="Organic Linen Chef Apron",
            slug="linen-chef-apron",
            category="Kitchen",
            description="100% European flax washed linen apron with adjustable neck strap and deep utility pockets.",
            price=38.00,
            currency="USD",
            in_stock=True,
            rating=4.7,
            image_url="/products/linen_apron.jpg",
            meta_info={"material": "Organic Linen"},
        ),
        Product(
            id="prod_home_03",
            merchant_id=MCH_HOME_ID,
            name="Aromatherapy Soy Candle (Amber & Teak)",
            slug="soy-candle-amber",
            category="Home Décor",
            description="Hand-poured 10oz natural soy wax candle with lead-free cotton wick and 60-hour burn time.",
            price=26.50,
            currency="USD",
            in_stock=True,
            rating=4.8,
            image_url="/products/soy_candle.jpg",
            meta_info={"burn_hours": 60},
        ),
        Product(
            id="prod_home_04",
            merchant_id=MCH_HOME_ID,
            name="Artisan Acacia Wood Salad Bowl",
            slug="acacia-salad-bowl",
            category="Kitchen",
            description="Single-block carved solid acacia hardwood serving bowl with matching salad servers.",
            price=44.00,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/acacia_bowl.jpg",
            meta_info={"diameter_inches": 12},
        ),
        # MediaNest
        Product(
            id="prod_media_01",
            merchant_id=MCH_MEDIA_ID,
            name="MediaNest Stream Pass Unlimited (Monthly)",
            slug="stream-pass-monthly",
            category="Streaming",
            description="Ad-free 4K streaming access across movies, exclusive series, and documentary channels.",
            price=14.99,
            currency="USD",
            in_stock=True,
            rating=4.7,
            image_url="/products/stream_pass.jpg",
            meta_info={"billing": "monthly", "is_subscription": True},
        ),
        Product(
            id="prod_media_02",
            merchant_id=MCH_MEDIA_ID,
            name="MediaNest Audio Hi-Fi Tier (Annual)",
            slug="audio-hifi-annual",
            category="Music",
            description="Lossless FLAC audio streaming catalog with 100 million tracks and offline downloading.",
            price=79.99,
            currency="USD",
            in_stock=True,
            rating=4.8,
            image_url="/products/hifi_annual.jpg",
            meta_info={"billing": "annual", "is_subscription": True},
        ),
        Product(
            id="prod_media_03",
            merchant_id=MCH_MEDIA_ID,
            name="Indie Film Club Festival Pass",
            slug="indie-film-pass",
            category="Movies",
            description="Digital festival access to 50 curated international indie films and director Q&A sessions.",
            price=19.99,
            currency="USD",
            in_stock=True,
            rating=4.6,
            image_url="/products/film_pass.jpg",
            meta_info={"valid_days": 14},
        ),
        Product(
            id="prod_media_04",
            merchant_id=MCH_MEDIA_ID,
            name="MediaNest Family Bundle (Monthly)",
            slug="family-bundle-monthly",
            category="Streaming",
            description="Up to 6 independent family profiles with concurrent streaming and parental content filters.",
            price=22.99,
            currency="USD",
            in_stock=True,
            rating=4.9,
            image_url="/products/family_bundle.jpg",
            meta_info={"billing": "monthly", "is_subscription": True},
        ),
    ]
    db.add_all(products_data)
    await db.flush()

    # ----------------------------------------------------
    # 4. POLICIES & RAG CHUNKS (5 policies)
    # ----------------------------------------------------
    policies_def = [
        {
            "id": "pol_nova_assurance",
            "merchant_id": MCH_NOVA_ID,
            "title": "Nova Electronics Customer Assurance Policy v2.1",
            "policy_type": "REFUND",
            "version": 2,
            "rules": {"return_window_days": 30, "partial_refund_max_pct": 75, "damage_eligible": True, "autonomous_limit": 250.0},
            "content": """# Nova Electronics Customer Assurance Policy

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
Approved refunds are processed via PayPal back to the original funding source within 1 business day."""
        },
        {
            "id": "pol_urban_satisfaction",
            "merchant_id": MCH_URBAN_ID,
            "title": "UrbanFit 45-Day Performance Guarantee",
            "policy_type": "RETURN",
            "version": 1,
            "rules": {"return_window_days": 45, "free_exchanges": True, "hygiene_restriction": True, "autonomous_limit": 150.0},
            "content": """# UrbanFit 45-Day Performance Guarantee

## 1. 45-Day Trial Period
Try our gear for up to 45 days. If running shoes or apparel do not fit perfectly or meet performance standards, return or exchange for free.

## 2. Condition Guidelines
Shoes must show only light indoor or track wear. Apparel must be unwashed with tags where feasible. Water bottles and hygiene items must be unopened.

## 3. Instant Exchange
Exchanges for alternative shoe sizes or colorways ship immediately without wait times."""
        },
        {
            "id": "pol_travel_terms",
            "merchant_id": MCH_TRAVEL_ID,
            "title": "TravelHub Booking & Cancellation Framework",
            "policy_type": "WARRANTY",
            "version": 3,
            "rules": {"flight_grace_period_hours": 24, "hotel_notice_hours": 48, "non_refundable_after_window": True, "autonomous_limit": 500.0},
            "content": """# TravelHub Booking & Cancellation Framework

## 1. Flight Cancellation Windows
Airfare tickets can be fully cancelled without penalty within 24 hours of purchase under DOT consumer rules. Beyond 24 hours, airfare is strictly non-refundable and subject to airline travel credits only.

## 2. Hotel Lodging Terms
Hotel stays may be cancelled with full refund up to 48 hours prior to scheduled 15:00 check-in. Cancellations under 48 hours forfeit the first night room rate.

## 3. Insurance Activation
Travel insurance policies activate immediately upon purchase and cannot be refunded once travel dates begin."""
        },
        {
            "id": "pol_home_artisan",
            "merchant_id": MCH_HOME_ID,
            "title": "HomeCraft Artisan Lifetime Quality Pledge",
            "policy_type": "WARRANTY",
            "version": 1,
            "rules": {"breakage_guarantee_days": 60, "handmade_variance_allowed": True, "autonomous_limit": 200.0},
            "content": """# HomeCraft Artisan Lifetime Quality Pledge

## 1. Ceramic & Stoneware Transit Protection
Handmade ceramics that experience breakage or chipping during shipping are replaced at zero cost or granted a full store refund within 60 days.

## 2. Natural Materials Variance
Handcrafted wood and linen items naturally exhibit subtle grain and dye variations. These are authentic hallmarks of artisan crafting rather than defects."""
        },
        {
            "id": "pol_media_digital",
            "merchant_id": MCH_MEDIA_ID,
            "title": "MediaNest Digital Content & Billing Policy",
            "policy_type": "SPENDING",
            "version": 2,
            "rules": {"duplicate_billing_auto_refund": True, "cancel_anytime": True, "autonomous_limit": 50.0},
            "content": """# MediaNest Digital Content & Billing Policy

## 1. Subscription Billing & Cancellation
All subscriptions renew automatically each month or year. You may cancel at any moment from your account dashboard without cancellation penalties.

## 2. Duplicate Billing Safeguard
If a technical glitch causes a duplicate transaction for the same subscription period, our automated system or customer service immediately issues a full refund for the duplicate charge."""
        },
    ]

    for p in policies_def:
        pol = MerchantPolicy(
            id=p["id"],
            merchant_id=p["merchant_id"],
            title=p["title"],
            policy_type=p["policy_type"],
            raw_content=p["content"],
            status="PUBLISHED",
            version=p["version"],
            rules_json=p["rules"],
        )
        db.add(pol)

        # Chunk and index into vector store & database
        chunks = policy_chunker.chunk_document(p["content"], merchant_id=p["merchant_id"], title=p["title"])
        for c in chunks:
            vector_store.add_chunk(c)
            chunk_obj = PolicyChunk(
                policy_id=pol.id,
                merchant_id=p["merchant_id"],
                section_title=c.get("title", "Policy Section"),
                content=c["content"],
                embedding=vector_store.generate_embedding(c["content"]),
                chunk_metadata={"merchant_id": p["merchant_id"], "policy_title": p["title"]},
            )
            db.add(chunk_obj)
    await db.flush()

    # ----------------------------------------------------
    # 5. TRANSACTIONS (68 realistic transactions)
    # ----------------------------------------------------
    transactions_data: List[Transaction] = []
    events_data: List[TransactionEvent] = []

    # 5.1 Hero Transaction 1: Damaged Headphones (Nova Electronics)
    t_hero = Transaction(
        id=TX_HERO_ANC_ID,
        user_id=USER_ALEX_ID,
        merchant_id=MCH_NOVA_ID,
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
        meta_info={"source_type": "DEMO_SEED", "product_id": "prod_nova_01", "carrier": "UPS", "tracking": "1Z9999999999999999"},
        created_at=now - timedelta(days=12),
    )
    transactions_data.append(t_hero)
    events_data.append(TransactionEvent(
        transaction_id=t_hero.id,
        event_type="PAYPAL_PAYMENT_CAPTURED",
        actor="PAYPAL",
        description="PayPal payment captured successfully. Verified by PayPal read-back audit.",
        created_at=now - timedelta(days=12),
    ))

    # 5.2 Hero Transactions 2 & 3: Duplicate MediaNest Streaming Charges
    t_med1 = Transaction(
        id=TX_MEDIA_01_ID,
        user_id=USER_ALEX_ID,
        merchant_id=MCH_MEDIA_ID,
        merchant_name="MediaNest",
        paypal_order_id="6M829104PA102948X",
        paypal_capture_id="8C194820LK294819M",
        amount=14.99,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.12,
        risk_level="LOW",
        ai_summary="Monthly digital streaming subscription payment.",
        item_description="MediaNest Premium Streaming (Monthly)",
        meta_info={"source_type": "DEMO_SEED", "is_subscription": True, "product_id": "prod_media_01"},
        created_at=now - timedelta(days=3),
    )
    t_med2 = Transaction(
        id=TX_MEDIA_DUP_ID,
        user_id=USER_ALEX_ID,
        merchant_id=MCH_MEDIA_ID,
        merchant_name="MediaNest",
        paypal_order_id="7M829104PA102949Y",
        paypal_capture_id="9C194820LK294820N",
        amount=14.99,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.88,
        risk_level="HIGH",
        ai_summary="Potential duplicate charge detected: Identical amount ($14.99) charged within 4 minutes.",
        item_description="MediaNest Premium Streaming (Monthly)",
        meta_info={"source_type": "DEMO_SEED", "is_duplicate": True, "is_subscription": True, "product_id": "prod_media_01"},
        created_at=now - timedelta(days=3, minutes=-4),
    )
    transactions_data.extend([t_med1, t_med2])
    events_data.extend([
        TransactionEvent(
            transaction_id=t_med1.id,
            event_type="PAYPAL_PAYMENT_CAPTURED",
            actor="PAYPAL",
            description="Recurring subscription capture authorized.",
            created_at=now - timedelta(days=3),
        ),
        TransactionEvent(
            transaction_id=t_med2.id,
            event_type="ANOMALY_FLAGGED",
            actor="AGENT",
            description="Payment Guard detected duplicate window violation: identical amount charged within 4 minutes.",
            created_at=now - timedelta(days=3, minutes=-4),
        ),
    ])

    # 5.3 Hero Transaction 4: Expired TravelHub Flight (Alex Chen)
    t_travel = Transaction(
        id=TX_TRAVEL_EXP_ID,
        user_id=USER_ALEX_ID,
        merchant_id=MCH_TRAVEL_ID,
        merchant_name="TravelHub",
        paypal_order_id="8T102938TR492019Q",
        paypal_capture_id="2C948201KK482910V",
        amount=385.00,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.18,
        risk_level="LOW",
        ai_summary="Transcontinental economy airfare SFO to JFK.",
        item_description="Express Flight Booking (SFO -> JFK)",
        meta_info={"source_type": "DEMO_SEED", "product_id": "prod_travel_01", "booking_ref": "SKY-9842"},
        created_at=now - timedelta(days=45), # Far outside 24h window
    )
    transactions_data.append(t_travel)

    # 5.4 Hero Transaction 5: HomeCraft Dinner Set (Devin Cole)
    t_home = Transaction(
        id=TX_HOME_SET_ID,
        user_id=USER_DEVIN_ID,
        merchant_id=MCH_HOME_ID,
        merchant_name="HomeCraft",
        paypal_order_id="9H482019HC382910Z",
        paypal_capture_id="4C829102PP382910W",
        amount=128.00,
        currency="USD",
        status="CAPTURED",
        verification_status="VERIFIED",
        risk_score=0.15,
        risk_level="LOW",
        ai_summary="Handmade Stoneware Dinner Set 16-Piece ordered with gift wrap.",
        item_description="Handmade Stoneware Dinner Set (16-Piece)",
        meta_info={"source_type": "DEMO_SEED", "product_id": "prod_home_01"},
        created_at=now - timedelta(days=8),
    )
    transactions_data.append(t_home)

    # 5.5 Synthesize 63 additional diverse transactions across merchants and users
    random.seed(1337)
    all_users = [USER_ALEX_ID, USER_SARAH_ID, USER_MARCUS_ID, USER_ELENA_ID, USER_DEVIN_ID]
    merchant_catalog_map = {
        MCH_NOVA_ID: ("Nova Electronics", [("NovaCharge 100W GaN Fast Charger", 39.99), ("NovaPad Air Mechanical Keyboard", 119.50), ("Quantum 4K Ultra Gaming Monitor", 349.99)]),
        MCH_URBAN_ID: ("UrbanFit", [("UrbanFlex Seamless Yoga Mat Pro", 48.00), ("SpeedStride Carbon Running Shoes", 145.00), ("TitanGrip Resistance Band Set", 24.99), ("HydraPulse 32oz Bottle", 32.00)]),
        MCH_TRAVEL_ID: ("TravelHub", [("Boutique Hotel Stay 2 Nights", 240.00), ("Global Travel Guard Insurance", 45.00), ("Airport VIP Lounge One-Day Pass", 55.00)]),
        MCH_HOME_ID: ("HomeCraft", [("Organic Linen Chef Apron", 38.00), ("Aromatherapy Soy Candle", 26.50), ("Artisan Acacia Wood Salad Bowl", 44.00)]),
        MCH_MEDIA_ID: ("MediaNest", [("MediaNest Stream Pass Unlimited", 14.99), ("MediaNest Audio Hi-Fi Tier", 79.99), ("Indie Film Club Festival Pass", 19.99)]),
    }

    mch_ids = list(merchant_catalog_map.keys())
    for i in range(1, 64):
        m_id = random.choice(mch_ids)
        m_name, items = merchant_catalog_map[m_id]
        item_name, item_price = random.choice(items)
        u_id = random.choice(all_users)
        days_ago = random.randint(1, 58)
        tx_time = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # Inject occasional anomaly / high amount
        is_high = (random.random() < 0.08)
        if is_high:
            tx_amount = item_price * random.randint(4, 8)
            risk_score = round(random.uniform(0.72, 0.94), 2)
            risk_level = "HIGH"
            status = "CAPTURED"
            verification = "VERIFIED"
            summary = f"High velocity bulk order for {item_name} exceeding standard shopper threshold."
        else:
            tx_amount = item_price
            risk_score = round(random.uniform(0.02, 0.28), 2)
            risk_level = "LOW"
            status = "CAPTURED"
            verification = "VERIFIED"
            summary = f"Routine verified purchase of {item_name} from {m_name}."

        tx_obj = Transaction(
            id=f"tx_synth_{i:03d}",
            user_id=u_id,
            merchant_id=m_id,
            merchant_name=m_name,
            paypal_order_id=f"PAY-{random.randint(100000, 999999)}-{i:03d}",
            paypal_capture_id=f"CAP-{random.randint(100000, 999999)}-{i:03d}",
            amount=tx_amount,
            currency="USD",
            status=status,
            verification_status=verification,
            risk_score=risk_score,
            risk_level=risk_level,
            ai_summary=summary,
            item_description=item_name,
            meta_info={"source_type": "DEMO_SEED", "is_synthetic": True, "category": m_name},
            created_at=tx_time,
        )
        transactions_data.append(tx_obj)
        events_data.append(TransactionEvent(
            transaction_id=tx_obj.id,
            event_type="PAYPAL_PAYMENT_CAPTURED",
            actor="PAYPAL",
            description=f"Transaction settled via PayPal sandbox for ${tx_amount:.2f}.",
            created_at=tx_time,
        ))

    db.add_all(transactions_data)
    await db.flush()
    db.add_all(events_data)
    await db.flush()

    # ----------------------------------------------------
    # 6. RECLAIM CASES & EVIDENCE
    # ----------------------------------------------------
    rc_hero = ReclaimCase(
        id=RECLAIM_HERO_CASE_ID,
        transaction_id=TX_HERO_ANC_ID,
        user_id=USER_ALEX_ID,
        issue_type="DAMAGED_ITEM",
        description="The right ear cup arrived with a cracked polycarbonate casing and scuffed swivel joint from shipping impact.",
        status="AI_RECOMMENDED",
        proposed_resolution="PARTIAL_REFUND",
        recommended_amount=65.00,
        confidence_score=0.96,
        ai_reasoning="Customer uploaded clear photographic evidence of structural transit cracking. Nova Electronics Customer Assurance Policy Section 2 authorizes a partial refund up to 75% ($66.75) if retaining the unit. Recommending $65.00 settlement credit without requiring physical return.",
        policy_citation={"policy": "Nova Electronics Assurance v2.1", "section": "Section 2: Transit Defects", "max_allowable": 66.75},
        approval_status="PENDING",
        created_at=now - timedelta(days=2),
    )
    ev_hero = Evidence(
        id="ev_nova_headphone_damage",
        reclaim_case_id=rc_hero.id,
        file_name="damaged_headphone_earcup.jpg",
        file_type="image/jpeg",
        file_url="/uploads/damaged_headphone_earcup.jpg",
        evidence_type="PHOTO_DAMAGE",
        analysis_summary="Visual analysis detects 3.2cm hairline surface crack across polycarbonate hinge assembly. Matches customer report of carrier transit impact.",
        confidence_score=0.96,
        created_at=now - timedelta(days=2),
    )

    rc_dup = ReclaimCase(
        id=RECLAIM_DUP_CASE_ID,
        transaction_id=TX_MEDIA_DUP_ID,
        user_id=USER_ALEX_ID,
        issue_type="DUPLICATE_CHARGE",
        description="Identical $14.99 charge occurred 4 minutes after standard monthly renewal.",
        status="APPROVED",
        proposed_resolution="FULL_REFUND",
        recommended_amount=14.99,
        confidence_score=0.99,
        ai_reasoning="Automated Payment Guard duplicate charge confirmation. Exactly matches MediaNest Policy Section 2 duplicate safeguard.",
        policy_citation={"policy": "MediaNest Billing Policy", "section": "Section 2: Duplicate Billing Safeguard"},
        approval_status="USER_APPROVED",
        created_at=now - timedelta(days=3),
    )

    rc_travel = ReclaimCase(
        id=RECLAIM_TRAVEL_CASE_ID,
        transaction_id=TX_TRAVEL_EXP_ID,
        user_id=USER_ALEX_ID,
        issue_type="NOT_RECEIVED",
        description="Attempted cancellation requested 45 days after flight ticket purchase.",
        status="REJECTED",
        proposed_resolution="NO_ACTION",
        recommended_amount=0.00,
        confidence_score=0.98,
        ai_reasoning="Claim exceeds TravelHub 24-hour statutory non-refundable flight cancellation window per Section 1.",
        policy_citation={"policy": "TravelHub Framework", "section": "Section 1: 24-Hour Flight Cancellation Window"},
        approval_status="REJECTED",
        created_at=now - timedelta(days=5),
    )

    rc_home = ReclaimCase(
        id=RECLAIM_HOME_CASE_ID,
        transaction_id=TX_HOME_SET_ID,
        user_id=USER_DEVIN_ID,
        issue_type="WRONG_ITEM",
        description="One stoneware dinner plate was missing from the 16-piece set carton.",
        status="UNDER_REVIEW",
        proposed_resolution="REPLACEMENT",
        recommended_amount=32.00,
        confidence_score=0.91,
        ai_reasoning="Customer reported missing individual plate. HomeCraft Artisan Pledge guarantees replacement piece.",
        policy_citation={"policy": "HomeCraft Lifetime Pledge", "section": "Section 1: Breakage & Incomplete Shipment"},
        approval_status="PENDING",
        created_at=now - timedelta(days=1),
    )

    db.add_all([rc_hero, rc_dup, rc_travel, rc_home])
    await db.flush()
    db.add(ev_hero)
    await db.flush()

    # ----------------------------------------------------
    # 7. SUBSCRIPTIONS (4 active subscriptions)
    # ----------------------------------------------------
    subscriptions_data = [
        Subscription(
            id="sub_alex_media",
            user_id=USER_ALEX_ID,
            merchant_name="MediaNest",
            amount=14.99,
            currency="USD",
            billing_interval="MONTHLY",
            last_payment_date=(now - timedelta(days=3)).strftime("%Y-%m-%d"),
            next_expected_date=(now + timedelta(days=27)).strftime("%Y-%m-%d"),
            status="ACTIVE",
        ),
        Subscription(
            id="sub_devin_media",
            user_id=USER_DEVIN_ID,
            merchant_name="MediaNest",
            amount=14.99,
            currency="USD",
            billing_interval="MONTHLY",
            last_payment_date=(now - timedelta(days=14)).strftime("%Y-%m-%d"),
            next_expected_date=(now + timedelta(days=16)).strftime("%Y-%m-%d"),
            status="ACTIVE",
        ),
        Subscription(
            id="sub_elena_urban",
            user_id=USER_ELENA_ID,
            merchant_name="UrbanFit",
            amount=29.99,
            currency="USD",
            billing_interval="MONTHLY",
            last_payment_date=(now - timedelta(days=10)).strftime("%Y-%m-%d"),
            next_expected_date=(now + timedelta(days=20)).strftime("%Y-%m-%d"),
            status="ACTIVE",
        ),
        Subscription(
            id="sub_marcus_cloud",
            user_id=USER_MARCUS_ID,
            merchant_name="CloudFlow SaaS",
            amount=9.99,
            currency="USD",
            billing_interval="MONTHLY",
            last_payment_date=(now - timedelta(days=22)).strftime("%Y-%m-%d"),
            next_expected_date=(now + timedelta(days=8)).strftime("%Y-%m-%d"),
            status="ACTIVE",
        ),
    ]
    db.add_all(subscriptions_data)
    await db.flush()

    # ----------------------------------------------------
    # 8. NOTIFICATIONS (8 diverse alerts)
    # ----------------------------------------------------
    notifications_data = [
        Notification(
            id="notif_01",
            user_id=USER_ALEX_ID,
            title="RECLAIM Settlement Ready for Approval",
            message="A $65.00 partial refund resolution is awaiting your authorization for 'NovaSound ANC Pro Wireless Headphones'.",
            notification_type="PAYMENT_APPROVAL_REQUIRED",
            action_url="/reclaim",
            is_read=False,
            payload={"case_id": RECLAIM_HERO_CASE_ID, "amount": 65.00},
            created_at=now - timedelta(hours=3),
        ),
        Notification(
            id="notif_02",
            user_id=USER_ALEX_ID,
            title="Payment Guard Duplicate Blocked",
            message="Duplicate charge of $14.99 on MediaNest flagged and held for review.",
            notification_type="ANOMALY_DETECTED",
            action_url="/guard",
            is_read=True,
            payload={"transaction_id": TX_MEDIA_DUP_ID},
            created_at=now - timedelta(days=3),
        ),
        Notification(
            id="notif_03",
            user_id=USER_ALEX_ID,
            title="Refund Issued Successfully",
            message="$14.99 refunded back to your PayPal balance for duplicate MediaNest subscription.",
            notification_type="REFUND_COMPLETED",
            action_url="/transactions",
            is_read=True,
            created_at=now - timedelta(days=2),
        ),
        Notification(
            id="notif_04",
            user_id=USER_DEVIN_ID,
            title="Evidence Received for HomeCraft Case",
            message="Your claim regarding the missing dinner plate is being reviewed by the merchant.",
            notification_type="CASE_STATUS_UPDATE",
            action_url="/reclaim",
            is_read=False,
            payload={"case_id": RECLAIM_HOME_CASE_ID},
            created_at=now - timedelta(hours=12),
        ),
        Notification(
            id="notif_05",
            user_id=USER_SARAH_ID,
            title="New Merchant Dispute Assigned",
            message="A new customer assurance claim (#rc_nova_damage_hero) has been initiated for Nova Electronics.",
            notification_type="MERCHANT_DISPUTE",
            action_url="/merchant/reclaims",
            is_read=False,
            created_at=now - timedelta(hours=4),
        ),
        Notification(
            id="notif_06",
            user_id=USER_MARCUS_ID,
            title="System Security Audit Complete",
            message="PostgreSQL 16 audit scan confirmed 100% integrity across 20 tables.",
            notification_type="SECURITY_AUDIT",
            action_url="/admin/system",
            is_read=True,
            created_at=now - timedelta(days=1),
        ),
        Notification(
            id="notif_07",
            user_id=USER_ELENA_ID,
            title="UrbanFit Renewal Scheduled",
            message="Your monthly UrbanFit Training membership ($29.99) will renew on the 20th.",
            notification_type="SUBSCRIPTION_RENEWAL",
            action_url="/subscriptions",
            is_read=False,
            created_at=now - timedelta(days=1),
        ),
        Notification(
            id="notif_08",
            user_id=USER_ALEX_ID,
            title="High Value Purchase Policy Alert",
            message="Transaction of $385.00 on TravelHub matched travel policy bounds.",
            notification_type="POLICY_MATCH",
            action_url="/transactions",
            is_read=True,
            created_at=now - timedelta(days=45),
        ),
    ]
    db.add_all(notifications_data)
    await db.flush()

    # ----------------------------------------------------
    # 9. ML PREDICTIONS (Generate & persist for key transactions)
    # ----------------------------------------------------
    ml_service = get_ml_service()
    ml_service.ensure_models_ready()
    
    # Run predictions on hero transactions
    sample_targets = [t_hero, t_med1, t_med2, t_travel, t_home]
    for tx in sample_targets:
        await ml_service.predict_and_persist(db, tx, transactions_data[:10])

    # ----------------------------------------------------
    # 10. AGENT RUNS & TOOL CALLS (Multi-agent orchestration traces)
    # ----------------------------------------------------
    run_hero = AgentRun(
        id="run_reclaim_orchestrator_01",
        agent_name="ReclaimCoordinatorAgent",
        session_id="sess_reclaim_hero",
        user_id=USER_ALEX_ID,
        status="COMPLETED",
        latency_ms=1420,
        decision_summary="Recommendation formulated: Issue partial refund of $65.00 per Nova Assurance Policy Section 2. Photographic proof verified.",
        meta_info={
            "case_id": rc_hero.id,
            "transaction_id": t_hero.id,
            "orchestration_mode": "multi_agent_consensus",
            "confidence": 0.96,
        },
        created_at=now - timedelta(days=2),
    )
    db.add(run_hero)
    await db.flush()

    tool_calls = [
        AgentToolCall(
            run_id=run_hero.id,
            agent_name="ReclaimCoordinatorAgent",
            tool_name="evidence_vision_auditor",
            input_payload={"file_url": "/uploads/damaged_headphone_earcup.jpg", "expected_sku": "NE-ANC-PRO"},
            output_payload={"detected_damage": "surface_crack", "confidence": 0.96, "severity": "MODERATE_COSMETIC"},
            duration_ms=480,
            status="SUCCESS",
            is_approved="AUTO_ALLOWED",
        ),
        AgentToolCall(
            run_id=run_hero.id,
            agent_name="ReclaimCoordinatorAgent",
            tool_name="policy_rag_retriever",
            input_payload={"merchant_id": MCH_NOVA_ID, "query": "damaged in transit partial refund return window"},
            output_payload={"matched_section": "Section 2: Transit Defects", "max_partial_pct": 75, "restocking_exempt": True},
            duration_ms=210,
            status="SUCCESS",
            is_approved="AUTO_ALLOWED",
        ),
        AgentToolCall(
            run_id=run_hero.id,
            agent_name="ReclaimCoordinatorAgent",
            tool_name="policy_guard_evaluator",
            input_payload={"purchase_amount": 89.00, "proposed_credit": 65.00, "limit": 250.00},
            output_payload={"decision": "ALLOW_SETTLEMENT_PROPOSAL", "requires_human_approval": True},
            duration_ms=115,
            status="SUCCESS",
            is_approved="REQUIRES_HUMAN_APPROVAL",
        ),
    ]
    db.add_all(tool_calls)
    await db.flush()

    # ----------------------------------------------------
    # 11. SUPPLEMENTARY LINEAGE RECORDS (Actions, Verifications, Intents, Audits)
    # ----------------------------------------------------
    await _seed_supplementary_records(db, now)

    await db.commit()
    logger.info("Comprehensive seed completed successfully across all tables!")
    return await verify_demo_data(db)

async def _seed_supplementary_records(db: AsyncSession, now: datetime):
    """
    Seeds PurchaseIntent, PaymentAction, PaymentVerification, and AuditLog records.
    Completes end-to-end data lineage across PostgreSQL 16 tables.
    """
    # 1. Purchase Intents
    intent_alex = PurchaseIntent(
        id="intent_alex_headphones",
        user_id=USER_ALEX_ID,
        raw_prompt="I need noise-cancelling headphones for travel under 100 dollars",
        category="Electronics",
        purpose="Travel noise cancellation",
        budget_amount=100.00,
        currency="USD",
        approval_required=True,
        autonomy_level="SUPERVISED",
        status="FULFILLED",
    )
    intent_stream = PurchaseIntent(
        id="intent_alex_stream",
        user_id=USER_ALEX_ID,
        raw_prompt="Subscribe to MediaNest standard monthly streaming plan",
        category="Streaming",
        purpose="Entertainment",
        budget_amount=15.00,
        currency="USD",
        approval_required=False,
        autonomy_level="AUTONOMOUS",
        status="FULFILLED",
    )
    db.add_all([intent_alex, intent_stream])
    await db.flush()

    # 2. Payment Actions
    actions = [
        PaymentAction(
            id="act_hero_capture",
            transaction_id=TX_HERO_ANC_ID,
            action_type="CAPTURE",
            requested_amount=89.00,
            currency="USD",
            idempotency_key="idem_hero_capture_001",
            state="VERIFIED",
            paypal_reference_id="3C498126Y8012941P",
            meta_info={"order_id": "5O190127TN364715T", "source": "PAYPAL_SANDBOX"},
        ),
        PaymentAction(
            id="act_med1_capture",
            transaction_id=TX_MEDIA_01_ID,
            action_type="CAPTURE",
            requested_amount=14.99,
            currency="USD",
            idempotency_key="idem_med1_capture_001",
            state="VERIFIED",
            paypal_reference_id="8C194820LK294819M",
            meta_info={"order_id": "6M829104PA102948X", "source": "PAYPAL_SANDBOX"},
        ),
        PaymentAction(
            id="act_med2_capture",
            transaction_id=TX_MEDIA_DUP_ID,
            action_type="CAPTURE",
            requested_amount=14.99,
            currency="USD",
            idempotency_key="idem_med2_capture_001",
            state="VERIFIED",
            paypal_reference_id="9C194820LK294820N",
            meta_info={"order_id": "7M829104PA102949Y", "source": "PAYPAL_SANDBOX"},
        ),
        PaymentAction(
            id="act_med2_refund",
            transaction_id=TX_MEDIA_DUP_ID,
            action_type="REFUND",
            requested_amount=14.99,
            currency="USD",
            idempotency_key="idem_med2_refund_001",
            state="VERIFIED",
            paypal_reference_id="REF-9C194820LK294820N",
            meta_info={"capture_id": "9C194820LK294820N", "reason": "DUPLICATE_CHARGE"},
        ),
        PaymentAction(
            id="act_travel_capture",
            transaction_id=TX_TRAVEL_EXP_ID,
            action_type="CAPTURE",
            requested_amount=385.00,
            currency="USD",
            idempotency_key="idem_travel_capture_001",
            state="VERIFIED",
            paypal_reference_id="2C948201KK482910V",
            meta_info={"order_id": "8T102938TR492019Q", "source": "PAYPAL_SANDBOX"},
        ),
    ]
    db.add_all(actions)
    await db.flush()

    # 3. Payment Verifications
    verifications = [
        PaymentVerification(
            id="verif_hero_capture",
            payment_action_id="act_hero_capture",
            paypal_resource_id="3C498126Y8012941P",
            expected_amount=89.00,
            actual_amount=89.00,
            expected_currency="USD",
            actual_currency="USD",
            is_verified=True,
            verification_details={"status": "COMPLETED", "provider": "PAYPAL_SANDBOX", "audit_match": True},
        ),
        PaymentVerification(
            id="verif_med1_capture",
            payment_action_id="act_med1_capture",
            paypal_resource_id="8C194820LK294819M",
            expected_amount=14.99,
            actual_amount=14.99,
            expected_currency="USD",
            actual_currency="USD",
            is_verified=True,
            verification_details={"status": "COMPLETED", "provider": "PAYPAL_SANDBOX"},
        ),
        PaymentVerification(
            id="verif_med2_capture",
            payment_action_id="act_med2_capture",
            paypal_resource_id="9C194820LK294820N",
            expected_amount=14.99,
            actual_amount=14.99,
            expected_currency="USD",
            actual_currency="USD",
            is_verified=True,
            verification_details={"status": "COMPLETED", "provider": "PAYPAL_SANDBOX"},
        ),
        PaymentVerification(
            id="verif_med2_refund",
            payment_action_id="act_med2_refund",
            paypal_resource_id="REF-9C194820LK294820N",
            expected_amount=14.99,
            actual_amount=14.99,
            expected_currency="USD",
            actual_currency="USD",
            is_verified=True,
            verification_details={"status": "COMPLETED", "provider": "PAYPAL_SANDBOX", "refunded": True},
        ),
        PaymentVerification(
            id="verif_travel_capture",
            payment_action_id="act_travel_capture",
            paypal_resource_id="2C948201KK482910V",
            expected_amount=385.00,
            actual_amount=385.00,
            expected_currency="USD",
            actual_currency="USD",
            is_verified=True,
            verification_details={"status": "COMPLETED", "provider": "PAYPAL_SANDBOX"},
        ),
    ]
    db.add_all(verifications)
    await db.flush()

    # 4. Audit Logs
    audit_logs = [
        AuditLog(
            action="PURCHASE_INTENT_CREATED",
            actor_type="USER",
            actor_id=USER_ALEX_ID,
            resource_type="PURCHASE_INTENT",
            resource_id="intent_alex_headphones",
            details={"budget": 100.0, "prompt": "I need noise-cancelling headphones for travel under 100 dollars"},
            ip_address="127.0.0.1",
        ),
        AuditLog(
            action="ML_RISK_EVALUATION",
            actor_type="SYSTEM",
            actor_id="ml_engine_v1",
            resource_type="TRANSACTION",
            resource_id=TX_HERO_ANC_ID,
            details={"risk_score": 0.08, "anomaly_score": 0.04, "verdict": "ALLOW"},
            ip_address="127.0.0.1",
        ),
        AuditLog(
            action="PAYMENT_CAPTURED_AND_VERIFIED",
            actor_type="SYSTEM",
            actor_id="sys_paycore",
            resource_type="TRANSACTION",
            resource_id=TX_HERO_ANC_ID,
            details={"amount": 89.0, "currency": "USD", "merchant": "Nova Electronics", "order_id": "5O190127TN364715T"},
            ip_address="127.0.0.1",
        ),
        AuditLog(
            action="DUPLICATE_ANOMALY_FLAGGED",
            actor_type="SYSTEM",
            actor_id="payment_guard",
            resource_type="TRANSACTION",
            resource_id=TX_MEDIA_DUP_ID,
            details={"reason": "duplicate_within_4_minutes", "risk_score": 0.88},
            ip_address="127.0.0.1",
        ),
        AuditLog(
            action="REPAIR_REFUND_EXECUTED",
            actor_type="AGENT",
            actor_id="agent_reclaim",
            resource_type="TRANSACTION",
            resource_id=TX_MEDIA_DUP_ID,
            details={"amount": 14.99, "refund_id": "REF-9C194820LK294820N"},
            ip_address="127.0.0.1",
        ),
        AuditLog(
            action="SYSTEM_SECURITY_AUDIT",
            actor_type="SYSTEM",
            actor_id="security_auditor",
            resource_type="SYSTEM",
            resource_id="canonical_audit_scan",
            details={"status": "PASS", "subsystems_verified": 8},
            ip_address="127.0.0.1",
        ),
    ]
    db.add_all(audit_logs)
    await db.flush()

async def verify_demo_data(db: AsyncSession) -> Dict[str, Any]:
    """Inspects row counts and health across all entities in PostgreSQL."""
    stats = {
        "users": await db.scalar(select(func.count(User.id))),
        "merchants": await db.scalar(select(func.count(Merchant.id))),
        "products": await db.scalar(select(func.count(Product.id))),
        "merchant_policies": await db.scalar(select(func.count(MerchantPolicy.id))),
        "policy_chunks": await db.scalar(select(func.count(PolicyChunk.id))),
        "transactions": await db.scalar(select(func.count(Transaction.id))),
        "transaction_events": await db.scalar(select(func.count(TransactionEvent.id))),
        "reclaim_cases": await db.scalar(select(func.count(ReclaimCase.id))),
        "evidence": await db.scalar(select(func.count(Evidence.id))),
        "subscriptions": await db.scalar(select(func.count(Subscription.id))),
        "notifications": await db.scalar(select(func.count(Notification.id))),
        "ml_model_versions": await db.scalar(select(func.count(MLModelVersion.id))),
        "ml_predictions": await db.scalar(select(func.count(MLPrediction.id))),
        "agent_runs": await db.scalar(select(func.count(AgentRun.id))),
        "agent_tool_calls": await db.scalar(select(func.count(AgentToolCall.id))),
        "purchase_intents": await db.scalar(select(func.count(PurchaseIntent.id))),
        "payment_actions": await db.scalar(select(func.count(PaymentAction.id))),
        "payment_verifications": await db.scalar(select(func.count(PaymentVerification.id))),
        "audit_logs": await db.scalar(select(func.count(AuditLog.id))),
        "webhook_events": await db.scalar(select(func.count(WebhookEvent.id))),
    }
    logger.info("Seed verification complete: %s", stats)
    return stats
