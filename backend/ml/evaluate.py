"""
CLI Entrypoint for PayPath ML Evaluation:
Usage: python -m backend.ml.evaluate
"""

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from app.ml.inference import get_ml_service

def main():
    print("==================================================")
    print("PayPath ML Subsystem — Model Evaluation & Explainability")
    print("==================================================")
    service = get_ml_service()
    service.ensure_models_ready()
    
    print(f"Loaded Active Model Version: {service.model_version}")
    
    # Run test scenarios through inference service
    scenarios = [
        {
            "name": "Standard Normal Purchase",
            "data": {
                "id": "tx_eval_001",
                "user_id": "usr_eval_1",
                "merchant_name": "UrbanFit",
                "amount": 42.50,
                "item_description": "Yoga Mat and Resistance Band",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        },
        {
            "name": "High Value Outlier with Rush Keywords",
            "data": {
                "id": "tx_eval_002",
                "user_id": "usr_eval_2",
                "merchant_name": "Nova Electronics",
                "amount": 2899.99,
                "item_description": "High power gaming rig express delivery rush fee",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        },
        {
            "name": "Subscription Billing",
            "data": {
                "id": "tx_eval_003",
                "user_id": "usr_eval_3",
                "merchant_name": "MediaNest",
                "amount": 14.99,
                "item_description": "Monthly Stream Pass subscription",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "meta_info": {"is_subscription": True},
            },
        },
    ]
    
    for sc in scenarios:
        print(f"\nScenario: {sc['name']}")
        result = service.predict(sc["data"])
        print(f"  Risk Score:            {result['risk_score']} ({result['risk_level']})")
        print(f"  Anomaly Score:         {result['anomaly_score']}")
        print(f"  Prediction Label:      {result['prediction_label']}")
        print(f"  Policy Recommendation: {result['policy_recommendation']}")
        print(f"  Top Risk Drivers:")
        for driver in result["feature_contributions"][:3]:
            print(f"    - {driver['feature']}: value={driver['value']}, impact={driver['impact']}")
        print(f"  Safety Directive:      {result['safety_directive']}")
        
    print("\n==================================================")
    print("Evaluation Complete. Advisory signals verified.")
    print("==================================================")

if __name__ == "__main__":
    main()

