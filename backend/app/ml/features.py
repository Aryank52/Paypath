"""
Deterministic Feature Engineering Pipeline for PayPath Transactions.
Extracts numerical and categorical features for XGBoost risk classification and Isolation Forest anomaly detection.

CRITICAL SAFETY & INTEGRITY RULE:
NO DATA LEAKAGE: Never use post-outcome fields (e.g. refund_completed, dispute_outcome, chargeback_id).
All features represent the exact state at the moment of authorization / evaluation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd

FEATURE_NAMES = [
    "amount",
    "velocity_24h",
    "velocity_7d",
    "amount_velocity_24h",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "user_avg_amount_ratio",
    "merchant_risk_historical",
    "is_subscription",
    "high_risk_mcc",
    "duplicate_window_match",
]

# Baseline historical merchant risk priors
MERCHANT_RISK_PRIORS: Dict[str, float] = {
    "nova electronics": 0.18,
    "urbanfit": 0.08,
    "travelhub": 0.22,
    "homecraft": 0.05,
    "medianest": 0.06,
    "digital gadgets co": 0.15,
    "streamflex media": 0.05,
    "cloudflow saas": 0.03,
    "fitpulse wear": 0.09,
}

HIGH_RISK_KEYWORDS = [
    "gift card", "crypto", "wire", "express delivery", "rush fee",
    "high power gaming rig", "precious metals", "overseas booking"
]

def parse_iso_or_datetime(val: Any) -> datetime:
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val
    if isinstance(val, str):
        try:
            cleaned = val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass
    return datetime.now(timezone.utc)

def extract_features_from_dict(
    tx_data: Dict[str, Any],
    history_txs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, float]:
    """
    Extracts a feature dictionary from a single transaction dictionary and historical context.
    All returned values are floats for downstream ML models.
    """
    amount = float(tx_data.get("amount", 0.0))
    current_time = parse_iso_or_datetime(tx_data.get("created_at"))
    user_id = str(tx_data.get("user_id", ""))
    merchant_name = str(tx_data.get("merchant_name", "")).strip().lower()
    item_description = str(tx_data.get("item_description", "")).lower()
    
    # Time features
    hour_of_day = float(current_time.hour)
    day_of_week = float(current_time.weekday())
    is_weekend = 1.0 if day_of_week in [5, 6] else 0.0
    
    # Keyword / MCC risk indicator
    is_high_risk_keyword = 1.0 if any(kw in item_description for kw in HIGH_RISK_KEYWORDS) else 0.0
    high_risk_mcc = 1.0 if (amount > 1000.0 or is_high_risk_keyword == 1.0) else 0.0
    
    # Subscription indicator
    is_sub = 1.0 if (
        tx_data.get("meta_info", {}).get("is_subscription") is True
        or "subscription" in item_description
        or "monthly" in item_description
        or "annual" in item_description
    ) else 0.0
    
    # Merchant historical risk prior
    merchant_risk_historical = MERCHANT_RISK_PRIORS.get(merchant_name, 0.10)
    
    # User velocity & behavioral context from history
    velocity_24h = 0.0
    velocity_7d = 0.0
    amount_velocity_24h = 0.0
    user_amounts: List[float] = []
    duplicate_window_match = 0.0
    
    if history_txs:
        for prev in history_txs:
            # Skip comparing against itself
            if prev.get("id") and prev.get("id") == tx_data.get("id"):
                continue
            
            # Filter to same user
            if str(prev.get("user_id", "")) == user_id:
                prev_amt = float(prev.get("amount", 0.0))
                user_amounts.append(prev_amt)
                
                prev_time = parse_iso_or_datetime(prev.get("created_at"))
                diff_seconds = (current_time - prev_time).total_seconds()
                
                # Check for historical transactions strictly before or concurrent
                if 0 <= diff_seconds <= 86400: # 24h
                    velocity_24h += 1.0
                    amount_velocity_24h += prev_amt
                
                if 0 <= diff_seconds <= (7 * 86400): # 7d
                    velocity_7d += 1.0
                
                # Duplicate charge window check (same merchant, same amount within 3600 seconds)
                prev_merchant = str(prev.get("merchant_name", "")).strip().lower()
                if (
                    0 <= diff_seconds <= 3600
                    and prev_merchant == merchant_name
                    and abs(prev_amt - amount) < 0.01
                ):
                    duplicate_window_match = 1.0
    
    # Calculate user average amount ratio
    if user_amounts:
        avg_amt = sum(user_amounts) / len(user_amounts)
        user_avg_amount_ratio = float(amount / (avg_amt + 1e-4))
    else:
        user_avg_amount_ratio = 1.0 # Baseline for first-time transaction
    
    return {
        "amount": round(amount, 2),
        "velocity_24h": velocity_24h,
        "velocity_7d": velocity_7d,
        "amount_velocity_24h": round(amount_velocity_24h, 2),
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "user_avg_amount_ratio": round(user_avg_amount_ratio, 4),
        "merchant_risk_historical": round(merchant_risk_historical, 4),
        "is_subscription": is_sub,
        "high_risk_mcc": high_risk_mcc,
        "duplicate_window_match": duplicate_window_match,
    }

def extract_feature_vector(features: Dict[str, float]) -> List[float]:
    """Returns an ordered list of feature floats matching FEATURE_NAMES."""
    return [float(features.get(name, 0.0)) for name in FEATURE_NAMES]

def features_to_dataframe(feature_list: List[Dict[str, float]]) -> pd.DataFrame:
    """Converts a list of feature dictionaries to a strictly ordered pandas DataFrame."""
    df = pd.DataFrame(feature_list)
    for col in FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0.0
    return df[FEATURE_NAMES]

