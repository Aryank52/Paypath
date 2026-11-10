"""
PayPath Machine Learning Schemas (Pydantic v2).
Strongly-typed contracts for training, feature extraction, evaluation, model registry, and inference.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FeatureDriver(BaseModel):
    feature: str
    value: float
    global_importance: float
    impact: float

class MLPredictionRequest(BaseModel):
    amount: float = Field(gt=0, description="Transaction amount")
    merchant_name: str = Field(..., description="Merchant name")
    item_description: Optional[str] = Field(default="", description="Product or service description")
    user_id: Optional[str] = Field(default=None, description="Optional user ID for velocity features")
    is_subscription: Optional[bool] = Field(default=False, description="Whether transaction is a recurring billing")
    created_at: Optional[str] = Field(default=None, description="ISO-formatted transaction timestamp")

class MLPredictionResponse(BaseModel):
    model_name: str
    model_version: str
    risk_score: float
    anomaly_score: float
    risk_level: str
    prediction_label: str
    policy_recommendation: str
    feature_contributions: List[Dict[str, Any]]
    safety_directive: str
    timestamp: str

class MLModelVersionResponse(BaseModel):
    id: str
    model_name: str
    algorithm: str
    version: str
    training_dataset: str
    feature_version: str
    trained_at: datetime
    metrics: Dict[str, Any]
    status: str
    artifact_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MLFeatureMetadata(BaseModel):
    name: str
    description: str
    data_type: str
    leak_safe: bool = True

class MLFeatureCatalogResponse(BaseModel):
    feature_count: int
    feature_version: str
    features: List[MLFeatureMetadata]

class MLEvaluationReport(BaseModel):
    model_name: str
    algorithm: str
    version: str
    evaluated_at: str
    xgboost_metrics: Optional[Dict[str, Any]] = None
    isolation_forest_metrics: Optional[Dict[str, Any]] = None
    data_sufficiency: str
    status: str
