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

## 5. Live Production Diagnostic & Empirical Test Results

A dedicated diagnostic endpoint is available to platform administrators:
`GET /api/v1/system/storage-diagnostic`

### Empirical Findings:
- **Supabase Project Endpoint:** `https://btobwviqlcgydaxuphzh.supabase.co`
- **Key Type in Render Config:** Supabase Public (`anon`) API Key (`is_service_role: false`)
- **Bucket Creation:** Bucket `paypath-evidence` has been manually created in Supabase project `btobwviqlcgydaxuphzh`.
- **Live Upload Probe (`POST /api/v1/reclaim/cases/rc_nova_damage_hero/evidence`):**
  When uploading authentic PNG magic bytes (`\x89PNG\r\n\x1a\n...`), Supabase Storage REST API (`POST /storage/v1/object/paypath-evidence/...`) responds with HTTP 400:
  ```json
  {"statusCode":"403","error":"Unauthorized","message":"new row violates row-level security policy","code":"AccessDenied"}
  ```
- **Fail-Closed Verification:**
  The Render backend strictly refuses to write to ephemeral local container disk in production and returns:
  `HTTP 502 Bad Gateway: "Secure evidence cloud storage error: Production cloud storage failure: Supabase Storage returned 400: {"statusCode":"403","error":"Unauthorized","message":"new row violates row-level security policy","code":"AccessDenied"}"`
- **Gate 4 Status:** **BLOCKED** pending RLS policy authorization or `service_role` key configuration.

---

## 6. One-Click Unblocking Guide

To achieve 100% verified cloud persistence and unblock Gate 4:

1. **Option A (Supabase Dashboard — 30 seconds):**
   - Open [Supabase Dashboard](https://supabase.com/dashboard/project/btobwviqlcgydaxuphzh) -> **Storage** -> `paypath-evidence` -> **Policies**.
   - Add an RLS Policy on `storage.objects`: Allow `INSERT` and `SELECT` for `anon` and `authenticated` roles.
2. **Option B (Render Dashboard — 30 seconds, Recommended):**
   - In Supabase Dashboard -> **Project Settings** -> **API**, copy the `service_role` secret key.
   - In Render Dashboard -> PayPath Web Service -> **Environment**, update `SUPABASE_KEY` to the `service_role` key. The backend will bypass RLS and store/sign artifacts autonomously.



