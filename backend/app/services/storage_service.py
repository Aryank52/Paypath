"""
PayPath Storage Engine: Dual-Mode File Storage.
Supports Supabase Storage for production file persistence (private buckets + signed URLs)
with seamless fallback to secure local disk storage in development/test.
Authoritative transactional and relational records remain strictly in PostgreSQL 16.
"""

import os
import httpx
from typing import Optional, Dict, Any, Tuple
from app.core.config import settings
from app.core.observability import logger

class StorageService:
    def __init__(self):
        self.supabase_url = getattr(settings, "SUPABASE_URL", None)
        self.supabase_key = getattr(settings, "SUPABASE_KEY", None)
        self.bucket_name = getattr(settings, "SUPABASE_STORAGE_BUCKET", "paypath-evidence")
        self.local_upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "evidence")
        )
        os.makedirs(self.local_upload_dir, exist_ok=True)

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads an evidence file to private storage (Supabase in production, local in dev).
        Returns metadata including storage provider, path, and access URL.
        """
        dest_path = f"{user_id or 'shared'}/{filename}"

        if self.is_supabase_configured:
            try:
                base = self.supabase_url.rstrip("/")
                upload_endpoint = f"{base}/storage/v1/object/{self.bucket_name}/{dest_path}"
                headers = {
                    "Authorization": f"Bearer {self.supabase_key}",
                    "apikey": self.supabase_key,
                    "Content-Type": content_type,
                    "x-upsert": "true"
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(upload_endpoint, content=file_bytes, headers=headers)
                    resp.raise_for_status()

                # Generate a 1-hour signed URL for private bucket access
                signed_url = await self.create_signed_url(dest_path, expires_in=3600)
                logger.info(f"Uploaded file to Supabase Storage: bucket={self.bucket_name} path={dest_path}")
                return {
                    "provider": "SUPABASE_STORAGE",
                    "bucket": self.bucket_name,
                    "storage_path": dest_path,
                    "url": signed_url,
                    "is_private": True,
                    "size_bytes": len(file_bytes),
                    "content_type": content_type
                }
            except Exception as e:
                logger.warning(f"Supabase upload failed, falling back to secure local storage: {e}")

        # Local filesystem storage fallback
        user_folder = os.path.join(self.local_upload_dir, user_id or "shared")
        os.makedirs(user_folder, exist_ok=True)
        local_path = os.path.join(user_folder, filename)

        with open(local_path, "wb") as f:
            f.write(file_bytes)

        local_url = f"/api/v1/uploads/evidence/{user_id or 'shared'}/{filename}"
        logger.info(f"Stored file in secure local storage: {local_path}")
        return {
            "provider": "LOCAL_STORAGE",
            "bucket": "local-evidence",
            "storage_path": local_path,
            "url": local_url,
            "is_private": True,
            "size_bytes": len(file_bytes),
            "content_type": content_type
        }

    async def create_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Generates a temporary signed URL for private evidence access."""
        if not self.is_supabase_configured:
            return f"/api/v1/uploads/evidence/{storage_path}"

        try:
            base = self.supabase_url.rstrip("/")
            endpoint = f"{base}/storage/v1/object/sign/{self.bucket_name}/{storage_path}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "apikey": self.supabase_key,
                "Content-Type": "application/json"
            }
            payload = {"expiresIn": expires_in}
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(endpoint, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                signed_path = data.get("signedURL", "")
                return f"{base}/storage/v1{signed_path}"
        except Exception as e:
            logger.warning(f"Failed to generate Supabase signed URL: {e}")
            return f"/api/v1/uploads/evidence/{storage_path}"

storage_service = StorageService()
