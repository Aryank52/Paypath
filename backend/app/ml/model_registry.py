"""
PayPath ML Model Registry.
Manages lifecycle states and PostgreSQL persistence of trained models:
States: candidate -> validated -> active -> retired
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import MLModelVersion

ALLOWED_STATUSES = {"candidate", "validated", "active", "retired"}

class ModelRegistry:
    """Manages ML model lifecycle, versioning, metrics, and PostgreSQL registration."""

    @staticmethod
    async def register_model(
        session: AsyncSession,
        model_name: str,
        algorithm: str,
        version: str,
        training_dataset: str,
        feature_version: str,
        metrics: Dict[str, Any],
        artifact_path: str,
        status: str = "active",
    ) -> MLModelVersion:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {ALLOWED_STATUSES}")

        # If marking active, retire previous active versions of the same model
        if status == "active":
            await session.execute(
                update(MLModelVersion)
                .where(
                    MLModelVersion.model_name == model_name,
                    MLModelVersion.status == "active",
                )
                .values(status="retired")
            )

        model_version = MLModelVersion(
            model_name=model_name,
            algorithm=algorithm,
            version=version,
            training_dataset=training_dataset,
            feature_version=feature_version,
            trained_at=datetime.now(timezone.utc),
            metrics=metrics,
            status=status,
            artifact_path=artifact_path,
        )
        session.add(model_version)
        await session.commit()
        await session.refresh(model_version)
        return model_version

    @staticmethod
    async def get_active_model(
        session: AsyncSession,
        model_name: str,
    ) -> Optional[MLModelVersion]:
        stmt = (
            select(MLModelVersion)
            .where(
                MLModelVersion.model_name == model_name,
                MLModelVersion.status == "active",
            )
            .order_by(MLModelVersion.trained_at.desc())
        )
        return (await session.execute(stmt)).scalars().first()

    @staticmethod
    async def list_models(
        session: AsyncSession,
        status: Optional[str] = None,
    ) -> List[MLModelVersion]:
        stmt = select(MLModelVersion).order_by(MLModelVersion.trained_at.desc())
        if status:
            stmt = stmt.where(MLModelVersion.status == status)
        return list((await session.execute(stmt)).scalars().all())

    @staticmethod
    async def transition_status(
        session: AsyncSession,
        model_id: str,
        new_status: str,
    ) -> Optional[MLModelVersion]:
        if new_status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of {ALLOWED_STATUSES}")

        stmt = select(MLModelVersion).where(MLModelVersion.id == model_id)
        model = (await session.execute(stmt)).scalar_one_or_none()
        if not model:
            return None

        model.status = new_status
        await session.commit()
        await session.refresh(model)
        return model

model_registry = ModelRegistry()
