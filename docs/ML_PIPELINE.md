# PayPath ML Intelligence Subsystem & Pipeline Specification

## 1. Executive Summary & Purpose

The PayPath Machine Learning (ML) Subsystem provides automated, quantitative transaction intelligence and behavioral anomaly detection across the PayPath commerce lifecycle.

Operating under the strict core philosophy:
> **Understand. Decide. Act. Verify.**

The ML layer's output is **strictly non-authoritative and advisory**. ML models emit probabilistic risk scores, anomaly percentiles, and explainability vectors that are fed directly into the deterministic **Policy Engine**. At no point does a machine learning prediction possess the authority to initiate financial movements, mutate account balances, or approve disbursements without deterministic policy clearance and human authorization.

---

## 2. Machine Learning Architecture

```text
               TRANSACTION INITIATION
                         │
                         ▼
             [ 12-Feature Extractor ]
           (Strict Post-Outcome Exclusion)
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
 [ Supervised XGBoost ]     [ Isolation Forest ]
  Risk Classification        Anomaly Detection
          │                             │
          ▼                             ▼
    Calibrated Risk               Anomaly Score
     Score (0.0 - 1.0)             (-0.5 - 0.5)
          │                             │
          └──────────────┬──────────────┘
                         ▼
             [ Real-Time Inference ]
             - Advisory Directive
             - Top Feature Impact Drivers
                         │
                         ▼
             [ Deterministic Policy ]
             - Allow / Review / Step-up MFA / Block
```

---

## 3. Deterministic 12-Feature Pipeline

PayPath implements an immutable 12-feature schema (`f12_v1`) engineered specifically for transaction risk and fraud detection. To eliminate **data leakage**, features are strictly calculated from transaction intent and prior historical context. Under no circumstances are post-settlement or dispute outcome fields included.

### Feature Dictionary

| # | Feature Name | Type | Description | Leakage Prevention |
|---|--------------|------|-------------|--------------------|
| 1 | `amount` | Float | Transaction gross amount in USD. | Point-in-time intent |
| 2 | `velocity_24h` | Integer | Count of transactions by this user in prior 24 hours. | Historical window only |
| 3 | `velocity_7d` | Integer | Count of transactions by this user in prior 7 days. | Historical window only |
| 4 | `amount_velocity_24h` | Float | Total USD volume spent by this user in prior 24 hours. | Historical window only |
| 5 | `hour_of_day` | Integer | UTC initiation hour (0 - 23). | Point-in-time |
| 6 | `day_of_week` | Integer | Day of week (0 = Monday, 6 = Sunday). | Point-in-time |
| 7 | `is_weekend` | Binary | 1 if Saturday or Sunday, else 0. | Point-in-time |
| 8 | `user_avg_amount_ratio`| Float | Ratio of current amount to user historical average purchase size. | Prior history only |
| 9 | `merchant_risk_historical` | Float | Historical merchant dispute and refund frequency prior. | Merchant track record |
| 10 | `is_subscription` | Binary | 1 if recurring subscription or interval billing, else 0. | Intent classification |
| 11 | `high_risk_mcc` | Binary | 1 for luxury electronics, rapid crypto, or wire transfer keywords. | Merchant catalog category |
| 12 | `duplicate_window_match` | Binary | 1 if identical amount was charged to same merchant within 1 hour. | Windowed intent check |

---

## 4. Models & Algorithms

### 4.1 Supervised Model: XGBoost Classifier (`xgboost-transaction-risk`)
- **Algorithm**: Extreme Gradient Boosting (`xgb.XGBClassifier`).
- **Objective**: `binary:logistic`.
- **Hyperparameters**: `n_estimators=100`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`.
- **Target Variable**: `is_risky` (Binary: 1 for elevated risk / dispute likelihood, 0 for normal).
- **Target Performance**: Accuracy $\ge 0.85$, ROC-AUC $\ge 0.80$, Precision $\ge 0.80$.

### 4.2 Unsupervised Model: Isolation Forest (`isolation-forest-anomaly`)
- **Algorithm**: Scikit-Learn `IsolationForest`.
- **Objective**: Multi-dimensional outlier and novel pattern isolation without supervision.
- **Hyperparameters**: `n_estimators=100`, `contamination=0.08`, `random_state=42`.
- **Scoring**: Negative decision function normalized to calibrated anomaly score ($0.0$ to $1.0$).

---

## 5. Temporal Dataset Splitting Strategy

To mirror true production fintech conditions and prevent temporal leakage, dataset splitting does **NOT** use random shuffling. Instead, transactions are ordered strictly by creation timestamp ascending:

$$\text{Train (70\%)} \longrightarrow \text{Validation (15\%)} \longrightarrow \text{Test (15\%) }$$

- **Train Set (Earliest 70%)**: Optimizes gradient-boosted tree splits and establishes normal isolation depths.
- **Validation Set (Next 15%)**: Evaluates early stopping and hyperparameter convergence.
- **Test Set (Latest 15%)**: Measures out-of-time generalization across unseen future distributions.

---

## 6. Model Registry & PostgreSQL Persistence

Trained models and their metadata are version-controlled in the PostgreSQL `ml_model_versions` table:

```sql
SELECT model_name, algorithm, version, status, 
       metrics->>'accuracy' as accuracy, 
       metrics->>'roc_auc' as roc_auc, 
       artifact_path 
FROM ml_model_versions 
ORDER BY created_at DESC;
```

Artifacts are persisted to `backend/artifacts/ml/`:
- `xgboost_risk_v1.0.0.joblib`
- `isolation_forest_anomaly_v1.0.0.joblib`
- `feature_metadata_v1.0.0.json`

---

## 7. Explainability & Feature Drivers

Every transaction scored by the ML Subsystem produces a transparent explainability vector detailing the top features contributing to the risk score:

```json
{
  "feature": "amount",
  "value": 1999.0,
  "global_importance": 0.1375,
  "impact": 0.6873
}
```

The UI renders this in the **ML Simulator & Explainability Console** with dynamic visual impact bars, ensuring users and merchant compliance teams understand why a transaction received a particular risk score.

---

## 8. Deterministic Policy Governance

The fundamental safety rule of PayPath is:

```text
ML Model (Advisory Score) ───► Policy Engine (Enforcement Rules) ───► Decision
                                        ▲
                                        │
                                Merchant Limits &
                                User Spend Guard
```

- If `risk_score < 0.35` and `anomaly_score < 0.50`: Recommendation `ALLOW`.
- If `risk_score` between `0.35` and `0.70`: Recommendation `REVIEW`.
- If `risk_score > 0.70` and `user_avg_amount_ratio > 2.5`: Recommendation `REQUIRE_MFA`.
- If `duplicate_window_match == 1.0` or `risk_score >= 0.85`: Recommendation `BLOCK`.

The Policy Engine may **tighten** restrictions based on merchant or user rules, but ML can never bypass a deterministic rule.

