"""
CLI Entrypoint for PayPath ML Training:
Usage: python -m backend.ml.train
"""

import asyncio
import sys
from app.core.database import AsyncSessionLocal
from app.ml.train import train_and_register_models

async def main():
    print("==================================================")
    print("PayPath ML Subsystem — Model Training & Registry")
    print("==================================================")
    print("Connecting to PostgreSQL 16 database...")
    async with AsyncSessionLocal() as session:
        print("Extracting features, splitting temporal dataset (70/15/15)...")
        print("Training XGBoost risk classifier & Isolation Forest...")
        result = await train_and_register_models(session)
        
        print("\nTraining completed successfully!")
        print(f"Status: {result['status']}")
        print(f"Model Version: {result['version']}")
        print(f"Feature Version: {result['feature_version']}")
        print("\n--- XGBoost Risk Classifier Metrics ---")
        for k, v in result["xgboost_metrics"].items():
            if k != "feature_importances":
                print(f"  {k}: {v}")
        print("\n--- Top Feature Importances ---")
        for feat, imp in sorted(
            result["xgboost_metrics"]["feature_importances"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:6]:
            print(f"  {feat:25s}: {imp:.4f}")
            
        print("\n--- Isolation Forest Anomaly Detection Metrics ---")
        for k, v in result["isolation_forest_metrics"].items():
            print(f"  {k}: {v}")
            
        print("\n--- Artifacts Written ---")
        for k, path in result["artifacts"].items():
            print(f"  {k:16s}: {path}")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())

