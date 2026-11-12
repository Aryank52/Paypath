# PayPath Comprehensive Demo Data & Seed Catalog

## 1. Overview & Seed System

The PayPath seed subsystem (`backend/app/services/seed_service.py` and `backend/scripts/seed.py`) populates a realistic, high-fidelity financial dataset across **14 PostgreSQL tables**.

Supported CLI actions:
```bash
# Idempotently seed database
python -m backend.scripts.seed --action=seed

# Clean reset and re-seed all tables
python -m backend.scripts.seed --action=reset

# Verify row counts and integrity
python -m backend.scripts.seed --action=verify
```

---

## 2. Seeded Personas & Access

Demo access credentials for seeded personas are managed privately for evaluators. Contact the project owner for credentials.

| User ID | Email | Full Name | Role | MFA Enabled | Persona Profile |
|---------|-------|-----------|------|-------------|-----------------|
| `usr_demo_shopper_01` | `demo@paypath.finance` | Alex Chen | `USER` | No | Primary demo user; frequent gadget and tech buyer. |
| `usr_demo_shopper_02` | `jordan.taylor@paypath.finance` | Jordan Taylor | `USER` | No | Budget-conscious fitness and wellness shopper. |
| `usr_demo_shopper_03` | `elena.rostova@paypath.finance` | Elena Rostova | `USER` | No | High-velocity travel and hospitality customer. |
| `usr_merchant_admin_01` | `sarah.jenkins@paypath.finance` | Sarah Jenkins | `MERCHANT_ADMIN` | Yes | Nova Electronics store administrator. |
| `usr_platform_admin_01` | `marcus.vance@paypath.finance` | Marcus Vance | `PLATFORM_ADMIN` | Yes | PayPath global compliance and risk officer. |

---

## 3. Verified Merchants & Catalogs

1. **Nova Electronics** (`mch_nova_electronics`)
   - Category: Audio, Computing & Consumer Electronics
   - Risk Tier: `LOW`
   - Products (4):
     - *NovaSound ANC Pro Wireless Headphones* ($89.00)
     - *NovaCharge 100W GaN Travel Charger* ($49.00)
     - *NovaCast 4K Ultra Streaming Stick* ($39.00)
     - *NovaTab Air 11-inch Tablet* ($329.00)
   - Policies: 30-day return policy; immediate replacement on damaged delivery; serial number verification.

2. **UrbanFit Apparel** (`mch_urbanfit`)
   - Category: Fitness, Footwear & Athleisure
   - Risk Tier: `LOW`
   - Products (4):
     - *UrbanFit CloudStride Running Shoes* ($119.00)
     - *UrbanFit Thermal Seamless Leggings* ($58.00)
     - *UrbanFit Performance Water Bottle 32oz* ($24.00)
     - *UrbanFit Ergonomic Yoga Mat* ($42.00)
   - Policies: 45-day unworn return window with tags attached; sanitary seal required on water bottles.

3. **TravelHub Global** (`mch_travelhub`)
   - Category: Travel, Flights & Accommodation
   - Risk Tier: `MEDIUM`
   - Products (4):
     - *Weekend City Escape Hotel Voucher* ($249.00)
     - *Priority Airport Lounge Access Pass* ($45.00)
     - *Global eSIM Unlimited 15-Day Data* ($35.00)
     - *TravelGuard Comprehensive Flight Insurance* ($29.00)
   - Policies: 24-hour free cancellation on lodging; non-refundable once eSIM activated.

4. **HomeCraft Studio** (`mch_homecraft`)
   - Category: Home Decor, Kitchenware & Artisanal Goods
   - Risk Tier: `LOW`
   - Products (4):
     - *Handcrafted Ceramic Dinner Set (12pc)* ($145.00)
     - *Artisan Pour-Over Coffee Dripper* ($34.00)
     - *Organic Cotton Woven Throw Blanket* ($65.00)
     - *Scented Botanical Soy Candle Trio* ($38.00)
   - Policies: 14-day return window; damaged ceramics replaced with photo proof.

5. **MediaNest Digital** (`mch_medianest`)
   - Category: Streaming, Software & Digital Content
   - Risk Tier: `LOW`
   - Products (4):
     - *MediaNest Premium 1-Month Streaming Pass* ($14.99)
     - *MediaNest AudioBooks 3-Credit Bundle* ($29.99)
     - *CloudBackup 1TB Annual Plan* ($59.99)
     - *DesignStudio Pro Monthly Subscription* ($24.99)
   - Policies: 7-day prorated refund on recurring subscriptions; instant digital license revocation upon dispute.

---

## 4. Key Pre-Configured Transactions & RECLAIM Scenarios

### Hero Scenario 1: Damaged Delivery & Autonomous RECLAIM
- **Transaction ID**: `tx_nova_anc_hero`
- **Merchant**: Nova Electronics
- **Amount**: $89.00 (NovaSound ANC Pro Wireless Headphones)
- **Status**: `CAPTURED` (Verified by PayPal)
- **RECLAIM Case ID**: `case_reclaim_hero_01`
- **Issue**: `DAMAGED_ITEM` (Ear cup cracked during transit).
- **Attached Evidence**: High-resolution damaged packaging photo verified with JPEG magic bytes.
- **RAG Policy Resolution**: Nova Electronics damaged goods policy prescribes $65.00 partial refund or full replacement.

### Hero Scenario 2: High Velocity Double Charge Detection
- **Transaction ID**: `tx_urbanfit_burst_01` & `tx_urbanfit_burst_02`
- **Merchant**: UrbanFit Apparel
- **Amount**: $119.00 charged twice within 3 minutes.
- **ML & Payment Guard Signal**: `duplicate_window_match = 1.0`, anomaly score `0.88`. Policy Engine triggers `REQUIRE_MFA` and alerts user.

### Hero Scenario 3: Recurring Digital Subscription Monitoring
- **Transaction ID**: `tx_medianest_sub_01`
- **Merchant**: MediaNest Digital
- **Amount**: $14.99 recurring monthly stream pass.
- **Status**: Active subscription managed under automated Spend Guard policies.

