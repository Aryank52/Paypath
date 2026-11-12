import io
import os
import re
import uuid
import zipfile
from typing import Tuple
from fastapi import HTTPException, UploadFile, status

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n", b"\x89PNG"],
    "image/webp": [b"RIFF"],
    "application/pdf": [b"%PDF"],
    "application/msword": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"]
}

EXTENSION_TO_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Strips path traversal attempts and special characters from uploaded file names."""
    # Remove directory paths
    base_name = os.path.basename(filename)
    # Remove null bytes
    base_name = base_name.replace("\x00", "")
    # Remove any dangerous characters
    cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    # Ensure non-empty
    if not cleaned or cleaned.startswith('.'):
        cleaned = f"upload_{uuid.uuid4().hex[:8]}.dat"
    return cleaned

async def validate_and_save_upload(file: UploadFile, subfolder: str = "evidence") -> Tuple[str, str, int, str]:
    """
    Validates file size, MIME type, and magic bytes.
    Saves file to secure target location and returns (saved_file_name, file_url, file_size, mime_type).
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename."
        )

    # 1. Sanitize filename & validate extension
    safe_name = sanitize_filename(file.filename)
    extension = os.path.splitext(safe_name)[1].lower()

    if extension not in EXTENSION_TO_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file format or spoofed extension. Allowed types: JPG, PNG, PDF, DOC, DOCX."
        )

    # 2. Read first chunk to check magic bytes
    header = await file.read(2048)
    if not header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # 3. Validate MIME type & magic bytes
    matched_type = None
    for mime, signatures in ALLOWED_MIME_TYPES.items():
        for sig in signatures:
            if header.startswith(sig):
                matched_type = mime
                break
        if matched_type:
            break

    # If MIME type doesn't match magic signature
    if not matched_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file format or spoofed extension. Allowed types: JPG, PNG, PDF, DOC, DOCX."
        )

    # Validate that extension aligns with verified magic type
    expected_mime = EXTENSION_TO_MIME.get(extension)
    if expected_mime and expected_mime != matched_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension does not match verified MIME magic signature."
        )

    # 4. Read remainder of file to enforce max size
    remainder = await file.read()
    total_size = len(header) + len(remainder)

    if total_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    full_bytes = header + remainder

    # 5. Deep container inspection for DOCX files
    if matched_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            with zipfile.ZipFile(io.BytesIO(full_bytes)) as zf:
                namelist = zf.namelist()
                has_content_types = "[Content_Types].xml" in namelist
                has_word_dir = any(name.startswith("word/") for name in namelist)
                if not (has_content_types and has_word_dir):
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Invalid DOCX file: Office Open XML document structure not found."
                    )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Invalid DOCX file: corrupt or invalid ZIP container."
            )

    # 6. Save with a secure random UUID prefix
    unique_file_name = f"{uuid.uuid4().hex}_{safe_name}"

    # Check for Supabase Storage in production
    from app.core.config import settings
    is_prod = getattr(settings, "APP_ENV", "development").lower() == "production"

    supabase_configured = bool(
        getattr(settings, "SUPABASE_URL", None) and
        (getattr(settings, "SUPABASE_SECRET_KEY", None) or getattr(settings, "SUPABASE_KEY", None))
    )

    if supabase_configured:
        try:
            from app.services.storage_service import storage_service
            res = await storage_service.upload_file(full_bytes, unique_file_name, matched_type, subfolder)
            return unique_file_name, res["url"], total_size, matched_type
        except Exception as e:
            from app.core.observability import logger
            logger.warning(f"Supabase upload failed: {e}")
            if is_prod:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Secure evidence cloud storage error: {str(e)}"
                )
    elif is_prod:
        # In production, ephemeral local storage is prohibited to prevent evidence loss across container restarts
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloud evidence storage (Supabase) is required in production. Ephemeral local storage is disabled."
        )

    target_dir = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, unique_file_name)

    # Ensure path stays within target_dir (prevent traversal)
    if not os.path.abspath(target_path).startswith(UPLOAD_DIR):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path traversal detected."
        )

    with open(target_path, "wb") as f:
        f.write(full_bytes)

    file_url = f"/uploads/{subfolder}/{unique_file_name}"
    return unique_file_name, file_url, total_size, matched_type

