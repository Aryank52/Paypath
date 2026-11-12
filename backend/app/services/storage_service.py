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
        self.local_upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "evidence")
        )
        os.makedirs(self.local_upload_dir, exist_ok=True)

    @property
    def supabase_url(self) -> Optional[str]:
        return getattr(settings, "SUPABASE_URL", None)

    @property
    def supabase_key(self) -> Optional[str]:
        return getattr(settings, "SUPABASE_KEY", None)

    @property
    def bucket_name(self) -> str:
        return getattr(settings, "SUPABASE_STORAGE_BUCKET", "paypath-evidence")

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    async def ensure_bucket_exists(self) -> Dict[str, Any]:
        """Verifies whether the target Supabase storage bucket exists; creates it if missing."""
        if not self.is_supabase_configured:
            return {"status": "NOT_CONFIGURED", "bucket": self.bucket_name}

        base = self.supabase_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                get_resp = await client.get(f"{base}/storage/v1/bucket/{self.bucket_name}", headers=headers)
                if get_resp.status_code == 200:
                    return {"status": "EXISTS", "bucket": self.bucket_name}

                # Attempt creation
                logger.info(f"Supabase bucket {self.bucket_name} not found (status {get_resp.status_code}). Provisioning private bucket...")
                create_resp = await client.post(
                    f"{base}/storage/v1/bucket",
                    headers={**headers, "Content-Type": "application/json"},
                    json={
                        "id": self.bucket_name,
                        "name": self.bucket_name,
                        "public": False
                    }
                )
                if create_resp.status_code in (200, 201):
                    logger.info(f"Supabase bucket {self.bucket_name} created successfully.")
                    return {"status": "CREATED", "bucket": self.bucket_name}
                elif create_resp.status_code in (400, 409) and "already exists" in create_resp.text.lower():
                    return {"status": "EXISTS", "bucket": self.bucket_name}
                else:
                    logger.warning(f"Failed to create Supabase bucket {self.bucket_name}: {create_resp.status_code} {create_resp.text}")
                    return {"status": "ERROR", "code": create_resp.status_code, "detail": create_resp.text}
        except Exception as e:
            logger.warning(f"Error checking/creating Supabase bucket: {e}")
            return {"status": "ERROR", "detail": str(e)}

    async def check_health(self) -> Dict[str, Any]:
        """Provides deep diagnostic telemetry on the storage subsystem."""
        if not self.is_supabase_configured:
            return {
                "configured": False,
                "provider": "LOCAL_STORAGE",
                "bucket": self.bucket_name,
                "status": "NOT_CONFIGURED"
            }

        base = self.supabase_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Check what buckets exist
                list_resp = await client.get(f"{base}/storage/v1/bucket", headers=headers)
                available_buckets = list_resp.json() if list_resp.status_code == 200 else f"HTTP {list_resp.status_code}: {list_resp.text}"

                resp = await client.get(f"{base}/storage/v1/bucket/{self.bucket_name}", headers=headers)
                bucket_status = resp.status_code
                bucket_data = resp.json() if resp.status_code == 200 else resp.text

                auto_created = False
                provisioning_result = None
                if bucket_status == 404 or (bucket_status == 400 and ("NoSuchBucket" in resp.text or "Bucket not found" in resp.text)):
                    provisioning_result = await self.ensure_bucket_exists()
                    if provisioning_result.get("status") in ("CREATED", "EXISTS"):
                        auto_created = True
                        bucket_status = 200
                        bucket_data = provisioning_result
                    else:
                        bucket_data = provisioning_result

                return {
                    "configured": True,
                    "provider": "SUPABASE_STORAGE",
                    "bucket": self.bucket_name,
                    "endpoint": base,
                    "available_buckets": available_buckets,
                    "bucket_status": bucket_status,
                    "auto_created": auto_created,
                    "provisioning_result": provisioning_result,
                    "details": bucket_data,
                    "status": "HEALTHY" if bucket_status == 200 else "DEGRADED"
                }
        except Exception as e:
            return {
                "configured": True,
                "provider": "SUPABASE_STORAGE",
                "bucket": self.bucket_name,
                "status": "ERROR",
                "error": str(e)
            }

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
                    if resp.status_code == 404 or (resp.status_code == 400 and ("NoSuchBucket" in resp.text or "Bucket not found" in resp.text)):
                        # Target bucket may not exist yet, attempt provisioning and retry once
                        await self.ensure_bucket_exists()
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
                logger.warning(f"Supabase upload failed: {e}")
                is_prod = getattr(settings, "APP_ENV", "development").lower() == "production"
                if is_prod:
                    logger.error(f"Production cloud storage failure: cannot store to ephemeral disk in production: {e}")
                    raise RuntimeError(f"Production cloud storage failure: {e}") from e

        # Local filesystem storage fallback (only allowed in non-production environments)
        is_prod = getattr(settings, "APP_ENV", "development").lower() == "production"
        if is_prod:
            raise RuntimeError("Cloud evidence storage (Supabase) is not configured in production.")
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
