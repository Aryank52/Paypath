"""
PayPath Machine Learning Subsystem
Provides supervised risk classification (XGBoost) and unsupervised anomaly detection (Isolation Forest),
with deterministic feature engineering, temporal train/val/test splitting, and model registry persistence.

SAFETY DIRECTIVE:
ML models output advisory scores and feature contributions to the Policy Engine.
ML models NEVER directly move money, change balances, or initiate refunds.
"""

from app.ml.features import FEATURE_NAMES, extract_features_from_dict, extract_feature_vector
from app.ml.inference import MLInferenceService, get_ml_service

__all__ = [
    "FEATURE_NAMES",
    "extract_features_from_dict",
    "extract_feature_vector",
    "MLInferenceService",
    "get_ml_service",
]

