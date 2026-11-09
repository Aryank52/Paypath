# PayPath File Upload & Evidence Ingestion Security

## Overview
The RECLAIM resolution center allows claimants to upload photographic evidence, scanned receipts, and diagnostic reports. Because file ingestion is a primary vector for remote code execution (RCE) and denial of service (DoS), PayPath implements multi-layer validation before saving or processing files.

---

## Security Verification Layers

### 1. Magic Byte Inspection
File extensions can be easily spoofed (e.g. naming a PHP script `receipt.jpg`). PayPath inspects the initial 2,048 bytes of every uploaded file for valid binary signatures:
- **JPEG**: Starts with `\xff\xd8\xff`
- **PNG**: Starts with `\x89PNG\r\n\x1a\n`
- **WEBP**: Starts with `RIFF` and contains `WEBP`
- **PDF**: Starts with `%PDF`

Any payload whose magic bytes fail to match one of the whitelisted signatures is rejected with `HTTP 415 Unsupported Media Type`.

### 2. Strict Size Ceilings
- Maximum allowed file size: **10 MB** (`10 * 1024 * 1024` bytes).
- Uploads exceeding this threshold are terminated immediately with `HTTP 413 Request Entity Too Large`.

### 3. Path Traversal & Filename Sanitization
- Filenames containing path separators (`/`, `\`, `..`), null bytes (`\x00`), or control characters are stripped.
- Filenames are normalized using regex `[^a-zA-Z0-9_.-]`.
- Files are assigned a random UUID prefix on disk (e.g., `5f43e1d0_damaged_earcup.jpg`) to avoid collisions or predictable resource location.
- Files are strictly validated to reside within the intended directory using `os.path.abspath(target_path).startswith(UPLOAD_DIR)`.

### 4. Isolated Static File Serving
- Uploaded files are served with `StaticFiles` with disabled execution permissions.
- MIME type headers are explicitly set by server (`image/jpeg`, `image/png`, `application/pdf`) to prevent browser MIME-sniffing vulnerabilities.

