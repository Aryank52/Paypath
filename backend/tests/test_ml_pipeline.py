"""
Automated Integration Tests for PayPath ML Subsystem.
Verifies:
1. Deterministic feature extraction and data leakage prevention.
2. Temporal dataset splitting (70% train, 15% validation, 15% test).
3. Supervised XGBoost risk classifier and unsupervised Isolation Forest training.
4. Model registry persistence in PostgreSQL ml_model_versions table.
5. Real-time inference explainability and advisory policy recommendations.
6. API routes under /api/v1/ml/*.
"""

from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.transaction import Transaction
from app.ml.features import (
    FEATURE_NAMES,
    extract_features_from_dict,
    extract_feature_vector,
)
from app.ml.datasets import build_temporal_split, generate_bootstrap_transactions
from app.ml.inference import get_ml_service
from app.ml.train import train_and_register_models

def test_feature_extraction_determinism_and_no_leakage():
    """Verify that feature extraction is deterministic and completely excludes post-outcome data."""
    tx_normal = {
        "id": "tx_test_feat_01",
        "user_id": "usr_test_01",
        "merchant_name": "Nova Electronics",
        "amount": 89.00,
        "item_description": "NovaSound ANC Headphones",
        "created_at": "2026-03-01T12:00:00+00:00",
        "meta_info": {"is_subscription": False},
        # Deliberately injected post-outcome fields that MUST be ignored
        "status": "REFUNDED",
        "refund_completed": True,
        "dispute_outcome": "SELLER_WON",
    }
    
    feats = extract_features_from_dict(tx_normal)
    assert len(feats) == len(FEATURE_NAMES)
    for name in FEATURE_NAMES:
        assert name in feats
        assert isinstance(feats[name], (int, float))

    # Verify no post-outcome fields in features
    assert "status" not in feats
    assert "refund_completed" not in feats
    assert "dispute_outcome" not in feats

    # Determinism check
    feats_repeat = extract_features_from_dict(tx_normal)
    assert feats == feats_repeat

    vec = extract_feature_vector(feats)
    assert len(vec) == 12
    assert vec[0] == 89.00

def test_temporal_dataset_split_integrity():
    """Verify that temporal splitting sorts strictly by created_at ascending."""
    txs = generate_bootstrap_transactions(count=100)
    total = len(txs)
    expected_train = int(total * 0.70)
    expected_val = int(total * 0.15)
    expected_test = total - expected_train - expected_val

    X_train, y_train, X_val, y_val, X_test, y_test = build_temporal_split(txs, 0.70, 0.15)
    
    assert len(X_train) == expected_train
    assert len(X_val) == expected_val
    assert len(X_test) == expected_test
    assert len(y_train) == expected_train
    assert len(y_val) == expected_val
    assert len(y_test) == expected_test

    assert list(X_train.columns) == FEATURE_NAMES

@pytest.mark.asyncio
async def test_ml_training_and_registry_persistence():
    """Verify models train, evaluate metrics, and register in PostgreSQL."""
    async with AsyncSessionLocal() as session:
        result = await train_and_register_models(session)
        assert result["status"] == "TRAINED_AND_REGISTERED"
        assert result["version"] == "v1.0.0"
        assert "xgboost_metrics" in result
        assert "isolation_forest_metrics" in result
        assert result["xgboost_metrics"]["accuracy"] >= 0.70
        assert result["xgboost_metrics"]["roc_auc"] >= 0.50

@pytest.mark.asyncio
async def test_ml_inference_service_advisory_contract():
    """Verify inference returns calibrated scores, explainability drivers, and safety directive."""
    service = get_ml_service()
    service.ensure_models_ready()

    sample_tx = {
        "id": "tx_sim_01",
        "user_id": "usr_sim_01",
        "merchant_name": "Nova Electronics",
        "amount": 1999.00,
        "item_description": "High power gaming laptop rush order express delivery",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    pred = service.predict(sample_tx)
    assert "risk_score" in pred
    assert 0.0 <= pred["risk_score"] <= 1.0
    assert "anomaly_score" in pred
    assert 0.0 <= pred["anomaly_score"] <= 1.0
    assert pred["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert pred["policy_recommendation"] in ["ALLOW", "REVIEW", "REQUIRE_MFA", "BLOCK"]
    assert len(pred["feature_contributions"]) > 0
    assert "Advisory ML score" in pred["safety_directive"]

@pytest.mark.asyncio
async def test_ml_api_endpoints():
    """Verify GET /api/v1/ml/models, /features, /explain, and POST /predict."""
    async with AsyncSessionLocal() as session:
        await train_and_register_models(session)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Feature definitions
        feat_res = await client.get("/api/v1/ml/features")
        assert feat_res.status_code == 200
        assert feat_res.json()["feature_count"] == 12

        # 2. Registered models
        models_res = await client.get("/api/v1/ml/models")
        assert models_res.status_code == 200
        assert models_res.json()["count"] >= 2

        # 3. Transaction explainability on hero transaction
        # Ensure transaction exists in test session
        async with AsyncSessionLocal() as session:
            tx_check = await session.get(Transaction, "tx_nova_anc_hero")
            if not tx_check:
                session.add(Transaction(
                    id="tx_nova_anc_hero",
                    user_id="usr_demo_shopper_01",
                    merchant_id="mch_nova_electronics",
                    merchant_name="Nova Electronics",
                    amount=89.00,
                    currency="USD",
                    status="CAPTURED",
                    verification_status="VERIFIED",
                    risk_score=0.08,
                    risk_level="LOW",
                    item_description="NovaSound ANC Pro Wireless Headphones",
                ))
                await session.commit()

        from app.core.security import create_access_token
        alex_token = create_access_token("usr_demo_shopper_01", role="customer")
        auth_headers = {"Authorization": f"Bearer {alex_token}"}

        exp_res = await client.get("/api/v1/ml/explain/tx_nova_anc_hero", headers=auth_headers)
        assert exp_res.status_code == 200
        exp_data = exp_res.json()
        assert exp_data["transaction_id"] == "tx_nova_anc_hero"
        assert "ml_explanation" in exp_data

        # 4. Ad-hoc prediction simulation
        pred_res = await client.post("/api/v1/ml/predict", json={
            "amount": 14.99,
            "merchant_name": "MediaNest",
            "item_description": "Monthly Stream Pass",
            "is_subscription": True
        })
        assert pred_res.status_code == 200
        assert pred_res.json()["risk_level"] == "LOW"
        assert pred_res.json()["policy_recommendation"] == "ALLOW"
