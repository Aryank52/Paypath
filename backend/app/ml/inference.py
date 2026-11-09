"""
Production ML Inference Service for PayPath.
Provides:
- Real-time XGBoost risk classification
- Isolation Forest anomaly detection
- Explainability via feature contribution rankings
- Advisory policy recommendations to the Policy Engine
- PostgreSQL persistence to ml_predictions table

SAFETY CONTRACT:
This service outputs advisory risk metrics only.
It NEVER executes financial transfers, refund payouts, or balance updates.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.features import (
    FEATURE_NAMES,
    extract_features_from_dict,
    features_to_dataframe,
)
from app.models.ml import MLPrediction
from app.models.transaction import Transaction

ARTIFACTS_DIR = Path("backend/artifacts/ml")
VERSION_TAG = "v1.0.0"

class MLInferenceService:
    def __init__(self):
        self.xgb_model = None
        self.iso_model = None
        self.metadata = {}
        self.model_version = VERSION_TAG
        self._load_models()

    def _load_models(self):
        """Attempts to load persisted model artifacts from disk."""
        xgb_path = ARTIFACTS_DIR / f"xgboost_risk_{self.model_version}.joblib"
        iso_path = ARTIFACTS_DIR / f"isolation_forest_anomaly_{self.model_version}.joblib"
        meta_path = ARTIFACTS_DIR / f"feature_metadata_{self.model_version}.json"

        if xgb_path.exists() and iso_path.exists():
            try:
                self.xgb_model = joblib.load(xgb_path)
                self.iso_model = joblib.load(iso_path)
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
            except Exception as e:
                # Log and prepare lazy initialization
                self.xgb_model = None
                self.iso_model = None

    def ensure_models_ready(self):
        """Lazy self-training if artifacts do not exist yet."""
        if self.xgb_model is None or self.iso_model is None:
            from app.ml.datasets import build_temporal_split, generate_bootstrap_transactions
            from app.ml.train import (
                train_xgboost_risk_model,
                train_isolation_forest_anomaly_model,
                ensure_artifacts_dir,
            )
            ensure_artifacts_dir()
            bootstrap = generate_bootstrap_transactions(count=150)
            X_train, y_train, X_val, y_val, X_test, y_test = build_temporal_split(bootstrap)
            self.xgb_model, _ = train_xgboost_risk_model(X_train, y_train, X_val, y_val, X_test, y_test)
            self.iso_model, _ = train_isolation_forest_anomaly_model(X_train, X_test)

    def predict(
        self,
        tx_data: Dict[str, Any],
        history_txs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Computes risk score, anomaly score, explainable feature drivers,
        and safe policy recommendations.
        """
        self.ensure_models_ready()
        
        # 1. Extract feature dictionary
        features = extract_features_from_dict(tx_data, history_txs)
        df_feat = features_to_dataframe([features])
        
        # 2. Supervised XGBoost Risk Score
        proba = float(self.xgb_model.predict_proba(df_feat)[:, 1][0])
        risk_score = round(max(0.0, min(1.0, proba)), 4)
        
        # 3. Unsupervised Isolation Forest Anomaly Score
        # Decision function is positive for inliers, negative for outliers
        # Normalize into 0.0 (normal) to 1.0 (highly anomalous)
        raw_anomaly = float(self.iso_model.decision_function(df_feat)[0])
        # Typical range is [-0.25, 0.25], center at 0
        norm_anomaly = 0.5 - (raw_anomaly * 2.0)
        anomaly_score = round(max(0.0, min(1.0, norm_anomaly)), 4)
        
        # 4. Feature Contributions / Explainability
        # Combine model global feature importance with feature values
        feature_importances = getattr(self.xgb_model, "feature_importances_", None)
        contributions: List[Dict[str, Any]] = []
        
        if feature_importances is not None:
            for feat_name, imp in zip(FEATURE_NAMES, feature_importances):
                val = float(features.get(feat_name, 0.0))
                # Heuristic impact: importance * scaled feature value
                impact = round(float(imp * min(val, 5.0)), 4)
                contributions.append({
                    "feature": feat_name,
                    "value": val,
                    "global_importance": round(float(imp), 4),
                    "impact": impact,
                })
            # Sort top drivers
            contributions.sort(key=lambda x: x["impact"], reverse=True)
        
        # 5. Determine Risk Level & Label
        if risk_score >= 0.85 or anomaly_score >= 0.85:
            risk_level = "CRITICAL"
            label = "HIGH_RISK"
        elif risk_score >= 0.65 or anomaly_score >= 0.65:
            risk_level = "HIGH"
            label = "ANOMALY" if anomaly_score >= 0.70 else "SUSPICIOUS"
        elif risk_score >= 0.35:
            risk_level = "MEDIUM"
            label = "SUSPICIOUS"
        else:
            risk_level = "LOW"
            label = "NORMAL"
            
        # 6. Safe Policy Recommendation (Advisory to Policy Engine)
        if risk_level == "CRITICAL":
            policy_rec = "BLOCK"
        elif risk_level == "HIGH":
            policy_rec = "REQUIRE_MFA" if features.get("amount", 0) > 500 else "REVIEW"
        elif risk_level == "MEDIUM":
            policy_rec = "REVIEW"
        else:
            policy_rec = "ALLOW"
            
        return {
            "model_name": "xgboost-transaction-risk",
            "model_version": self.model_version,
            "risk_score": risk_score,
            "anomaly_score": anomaly_score,
            "risk_level": risk_level,
            "prediction_label": label,
            "policy_recommendation": policy_rec,
            "feature_contributions": contributions[:5], # Top 5 drivers
            "all_features": features,
            "safety_directive": "Advisory ML score. Final execution governed strictly by Policy Engine and Human Approval.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def predict_and_persist(
        self,
        session: AsyncSession,
        transaction: Transaction,
        history: Optional[List[Transaction]] = None,
    ) -> MLPrediction:
        """Runs prediction on a Transaction model and saves record to PostgreSQL."""
        tx_dict = {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "merchant_name": transaction.merchant_name,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "verification_status": transaction.verification_status,
            "risk_score": float(transaction.risk_score),
            "risk_level": transaction.risk_level,
            "item_description": transaction.item_description or "",
            "created_at": transaction.created_at.isoformat() if transaction.created_at else datetime.now(timezone.utc).isoformat(),
            "meta_info": transaction.meta_info or {},
        }
        
        hist_dicts = []
        if history:
            for h in history:
                hist_dicts.append({
                    "id": h.id,
                    "user_id": h.user_id,
                    "merchant_name": h.merchant_name,
                    "amount": float(h.amount),
                    "created_at": h.created_at.isoformat() if h.created_at else "",
                    "meta_info": h.meta_info or {},
                })
        
        result = self.predict(tx_dict, hist_dicts)
        
        pred = MLPrediction(
            transaction_id=transaction.id,
            model_name=result["model_name"],
            model_version=result["model_version"],
            risk_score=result["risk_score"],
            anomaly_score=result["anomaly_score"],
            prediction_label=result["prediction_label"],
            feature_contributions={
                "top_drivers": result["feature_contributions"],
                "policy_recommendation": result["policy_recommendation"],
            },
            policy_recommendation=result["policy_recommendation"],
        )
        session.add(pred)
        await session.commit()
        await session.refresh(pred)
        return pred

# Singleton instance
_service_instance: Optional[MLInferenceService] = None

def get_ml_service() -> MLInferenceService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MLInferenceService()
    return _service_instance

