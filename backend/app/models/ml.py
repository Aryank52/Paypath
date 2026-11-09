from sqlalchemy import Column, String, Numeric, DateTime, JSON, ForeignKey
from app.models.base import TimeStampedModel

class MLModelVersion(TimeStampedModel):
    __tablename__ = "ml_model_versions"
    
    model_name = Column(String(100), nullable=False) # e.g. "xgboost-transaction-risk", "isolation-forest-anomaly"
    algorithm = Column(String(100), nullable=False)  # "XGBoost", "IsolationForest"
    version = Column(String(50), nullable=False)    # e.g. "v1.0.0"
    training_dataset = Column(String(255), nullable=False)
    feature_version = Column(String(50), nullable=False)
    trained_at = Column(DateTime(timezone=True), nullable=False)
    metrics = Column(JSON, default=dict) # precision, recall, f1, roc_auc, pr_auc
    status = Column(String(50), default="active", nullable=False) # candidate, active, retired
    artifact_path = Column(String(500), nullable=True)

class MLPrediction(TimeStampedModel):
    __tablename__ = "ml_predictions"
    
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    risk_score = Column(Numeric(5, 4), nullable=True)
    anomaly_score = Column(Numeric(5, 4), nullable=True)
    prediction_label = Column(String(50), nullable=False) # "NORMAL", "SUSPICIOUS", "ANOMALY"
    feature_contributions = Column(JSON, default=dict)
    policy_recommendation = Column(String(50), default="ALLOW", nullable=False) # "ALLOW", "REVIEW", "BLOCK"

