# PayPath Evidence Storage Architecture & E2E Verification

**Document Version:** 1.0.0  
**Storage Provider:** Supabase Cloud Storage (Private Bucket: `paypath-evidence`)  
**Fallback Strategy:** Fail-Closed in Production; Local Filesystem strictly restricted to Dev/Test  
**Validation Pipeline:** Filename Sanitization, Size Boundary Check, Magic-Byte Signature Verification, Private Bucket Signed URL Generation  

---

## 1. Storage Purpose & Security Architecture

In PayPath's RECLAIM dispute resolution system, users upload evidentiary documents (damaged item photographs, merchant delivery receipts, correspondence screenshots). Because dispute files may contain sensitive customer data or be used in financial dispute arbitration:
1. **Public Access Prohibited:** Evidence files are stored in a private Supabase bucket (`paypath-evidence`) with public read access disabled.
2. **Time-Limited Signed URLs:** Access to view or download evidence is granted via cryptographically signed URLs with a strict 3600-second (1-hour) expiration.
3. **Magic-Byte Signature Verification:** Extensions alone (such as `.png` or `.pdf`) are never trusted. File contents are inspected at the byte level before writing to storage.
4. **Path Traversal Defense:** Filenames are stripped of directory separators, null bytes, and non-alphanumeric characters, then prefixed with a cryptographically secure random UUID (`uuid.uuid4().hex`).

---

## 2. Magic-Byte Validation Protocol

Implemented in `backend/app/core/upload_security.py`:

```python
ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
    "application/pdf": [b"%PDF"]
}
```

### Verification Steps:
1. Read initial 2048 bytes of the uploaded file.
2. Cross-reference against `ALLOWED_MIME_TYPES` magic-byte signatures.
3. If byte signature fails, reject immediately with `415 Unsupported Media Type` before streaming remainder of payload.
4. Accumulate total size and reject if $> 10\text{ MB}$ with `413 Request Entity Too Large`.

---

## 3. Production Fail-Closed Implementation

In containerized production environments like Render, files written to the local disk are ephemeral and destroyed upon container restarts. If Supabase is unconfigured or encounters an API error, falling back to local disk would result in silent, irreversible data loss.

Therefore, `backend/app/core/upload_security.py` and `backend/app/services/storage_service.py` enforce:

```python
is_prod = getattr(settings, "APP_ENV", "development").lower() == "production"

if getattr(settings, "SUPABASE_URL", None) and getattr(settings, "SUPABASE_KEY", None):
    try:
        from app.services.storage_service import storage_service
        res = await storage_service.upload_file(full_bytes, unique_file_name, matched_type, subfolder)
        return unique_file_name, res["url"], total_size, matched_type
    except Exception as e:
        logger.warning(f"Supabase upload failed: {e}")
        if is_prod:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Secure evidence cloud storage is temporarily unavailable. Upload could not be verified."
            )
elif is_prod:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Cloud evidence storage (Supabase) is required in production. Ephemeral local storage is disabled."
    )
```

---

## 4. End-to-End Test Verification

The upload pipeline and security barriers are rigorously validated by the automated test suite:

- `test_mfa_and_upload_security.py::test_file_upload_security_magic_bytes`:
  - Valid PNG with authentic `\x89PNG` header: **ACCEPTED (200 OK)**.
  - Spoofed `.pdf` containing raw executable or text bytes: **REJECTED (415 Unsupported Media Type)**.
  - Path traversal attack string `../../etc/passwd`: **SANITIZED to `upload_<uuid>.dat`**.
  - File size $> 10\text{ MB}$: **REJECTED (413 Request Entity Too Large)**.

---

## 5. Live Production Diagnostic & Bucket Provisioning

A dedicated diagnostic endpoint is available to platform administrators:
`GET /api/v1/system/storage-diagnostic`

### Empirical Findings:
- **Supabase Project Endpoint:** `https://btobwviqlcgydaxuphzh.supabase.co`
- **Key Type in Render Config:** Supabase Public (`anon`) API Key
- **Directory Probe (`GET /storage/v1/bucket`):** Returned HTTP 200 with `available_buckets: []` (no buckets provisioned yet in project).
- **Auto-Provisioning Response:** When the backend attempts automated bucket creation (`POST /storage/v1/bucket`), Supabase returns `403 Forbidden` (`{"statusCode":"403","error":"Unauthorized","message":"new row violates row-level security policy","code":"AccessDenied"}`) because creating storage buckets in Supabase requires administrative RLS bypass (`service_role` key) or manual dashboard creation.

### One-Click Activation Guide:
To complete evidence uploads in production, perform one of the following:
1. **Option A (Supabase Dashboard — 30 seconds):**
   - Open [Supabase Dashboard](https://supabase.com/dashboard/project/btobwviqlcgydaxuphzh) -> **Storage**.
   - Click **New Bucket**, name it `paypath-evidence`, and set it to **Private** (or add an insert policy for authenticated users).
2. **Option B (Render Dashboard — 30 seconds):**
   - In Supabase Dashboard -> **Project Settings** -> **API**, copy the `service_role` secret key.
   - In Render Dashboard -> PayPath Web Service -> **Environment**, update `SUPABASE_KEY` to the `service_role` key. The backend's automated `ensure_bucket_exists` will auto-create and manage `paypath-evidence` automatically.


