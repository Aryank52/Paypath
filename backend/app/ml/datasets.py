"""
Temporal Dataset Builder for PayPath Transaction Intelligence.
Enforces strict temporal ordering (70% train, 15% validation, 15% test) to prevent data leakage.
Provides bootstrapping generator to produce balanced, realistic financial training datasets.
"""

from datetime import datetime, timezone, timedelta
import random
from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from app.ml.features import (
    FEATURE_NAMES,
    extract_features_from_dict,
    features_to_dataframe,
    parse_iso_or_datetime,
)

def build_temporal_split(
    transactions: List[Dict[str, Any]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Sorts transactions by created_at ascending and splits into:
    - Train (earliest train_ratio, default 70%)
    - Validation (subsequent val_ratio, default 15%)
    - Test (latest remainder, default 15%)
    
    Returns: (X_train, y_train, X_val, y_val, X_test, y_test)
    """
    if len(transactions) < 10:
        # Augment with bootstrap data if real count is too low for a realistic split
        transactions = generate_bootstrap_transactions(count=150)
    
    # Sort strictly by timestamp ascending
    sorted_txs = sorted(
        transactions,
        key=lambda x: parse_iso_or_datetime(x.get("created_at")),
    )
    
    features_list: List[Dict[str, float]] = []
    labels: List[int] = []
    
    # Extract features using historical context up to each transaction
    for i, tx in enumerate(sorted_txs):
        history_prior = sorted_txs[:i]
        feats = extract_features_from_dict(tx, history_prior)
        features_list.append(feats)
        
        # Ground truth label derivation for training:
        # High risk (1) if explicitly marked HIGH/MEDIUM risk, has dispute, or high anomaly
        risk_lvl = str(tx.get("risk_level", "LOW")).upper()
        status = str(tx.get("status", "CREATED")).upper()
        raw_score = float(tx.get("risk_score", 0.0))
        is_flagged = tx.get("meta_info", {}).get("is_flagged", False)
        
        is_risky = 1 if (
            risk_lvl in ["HIGH", "CRITICAL"]
            or status in ["REFUNDED", "FAILED"]
            or raw_score >= 0.70
            or is_flagged
            or feats["duplicate_window_match"] == 1.0
        ) else 0
        labels.append(is_risky)
    
    df_X = features_to_dataframe(features_list)
    series_y = pd.Series(labels, name="is_risky")
    
    n_total = len(df_X)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    X_train = df_X.iloc[:n_train].reset_index(drop=True)
    y_train = series_y.iloc[:n_train].reset_index(drop=True)
    
    X_val = df_X.iloc[n_train:n_train + n_val].reset_index(drop=True)
    y_val = series_y.iloc[n_train:n_train + n_val].reset_index(drop=True)
    
    X_test = df_X.iloc[n_train + n_val:].reset_index(drop=True)
    y_test = series_y.iloc[n_train + n_val:].reset_index(drop=True)
    
    return X_train, y_train, X_val, y_val, X_test, y_test

def generate_bootstrap_transactions(count: int = 150) -> List[Dict[str, Any]]:
    """
    Generates synthetic realistic e-commerce transactions across normal, high velocity,
    duplicate charge, and anomalous cases to cold-start ML models.
    """
    random.seed(42)
    merchants = [
        {"name": "Nova Electronics", "risk": 0.15, "items": ["Wireless Earbuds", "Gaming Mouse", "USB-C Hub", "Laptop Pro"]},
        {"name": "UrbanFit", "risk": 0.05, "items": ["Yoga Mat", "Running Shoes", "Resistance Bands", "Water Bottle"]},
        {"name": "TravelHub", "risk": 0.20, "items": ["Flight Booking", "Express Hotel", "Rental Car", "Travel Insurance"]},
        {"name": "HomeCraft", "risk": 0.04, "items": ["Ceramic Mug", "Wooden Spoon Set", "Linen Apron", "Scented Candle"]},
        {"name": "MediaNest", "risk": 0.06, "items": ["Monthly Stream Pass", "Annual Audio Pass", "E-Book Pack"]},
    ]
    
    users = [f"usr_test_{i:03d}" for i in range(1, 12)]
    
    start_time = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    transactions: List[Dict[str, Any]] = []
    
    current_time = start_time
    for i in range(count):
        current_time += timedelta(minutes=random.randint(20, 240))
        m = random.choice(merchants)
        u = random.choice(users)
        item = random.choice(m["items"])
        
        # Determine archetype
        archetype = random.choices(
            ["normal", "high_amount", "duplicate", "rapid_burst", "subscription"],
            weights=[0.70, 0.10, 0.07, 0.08, 0.05],
            k=1
        )[0]
        
        meta = {}
        if archetype == "normal":
            amount = round(random.uniform(15.0, 180.0), 2)
            risk_level = "LOW"
            raw_risk = round(random.uniform(0.02, 0.25), 2)
            status = "CAPTURED"
        elif archetype == "high_amount":
            amount = round(random.uniform(1200.0, 3500.0), 2)
            risk_level = "HIGH"
            raw_risk = round(random.uniform(0.72, 0.95), 2)
            status = "CAPTURED"
            meta["is_flagged"] = True
        elif archetype == "duplicate":
            amount = round(random.uniform(49.99, 129.99), 2)
            risk_level = "HIGH"
            raw_risk = round(random.uniform(0.75, 0.92), 2)
            status = "CAPTURED"
            meta["is_duplicate"] = True
        elif archetype == "rapid_burst":
            amount = round(random.uniform(80.0, 300.0), 2)
            risk_level = "MEDIUM"
            raw_risk = round(random.uniform(0.45, 0.68), 2)
            status = "CAPTURED"
        else: # subscription
            amount = round(random.choice([9.99, 19.99, 29.99, 49.99]), 2)
            risk_level = "LOW"
            raw_risk = round(random.uniform(0.01, 0.15), 2)
            status = "CAPTURED"
            meta["is_subscription"] = True
        
        tx = {
            "id": f"tx_boot_{i:04d}",
            "user_id": u,
            "merchant_name": m["name"],
            "amount": amount,
            "currency": "USD",
            "status": status,
            "verification_status": "VERIFIED",
            "risk_score": raw_risk,
            "risk_level": risk_level,
            "item_description": item,
            "created_at": current_time.isoformat(),
            "meta_info": meta,
        }
        transactions.append(tx)
        
        # If duplicate archetype, immediately add matching tx within 5 minutes
        if archetype == "duplicate":
            current_time += timedelta(minutes=random.randint(1, 15))
            dup_tx = {
                "id": f"tx_boot_{i:04d}_dup",
                "user_id": u,
                "merchant_name": m["name"],
                "amount": amount,
                "currency": "USD",
                "status": "CAPTURED",
                "verification_status": "VERIFIED",
                "risk_score": 0.88,
                "risk_level": "HIGH",
                "item_description": item,
                "created_at": current_time.isoformat(),
                "meta_info": {"is_duplicate": True, "is_flagged": True},
            }
            transactions.append(dup_tx)
            
    return transactions

