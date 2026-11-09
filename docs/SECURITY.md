# PayPath Security Architecture & Hardening Specification

## 1. Security Core Principles
1. **Zero Secret Leakage:** PayPal Client Secret, webhook keys, database passwords, and JWT secret keys reside strictly in backend environment variables. The frontend bundle never receives API secrets.
2. **Defensive AI Engineering:** AI agents operate under least privilege. They cannot directly execute financial mutations or modify database records without going through deterministic validation gates.
3. **Dual-Phase Mutation Verification:** To prevent optimistic UI updates and state divergence, every capture and refund is re-verified by querying PayPal directly.
4. **Authoritative Ledger:** PostgreSQL 16 is the single system of record; optimistic in-memory states are strictly forbidden for financial balances.

---

## 2. Authentication & Authorization Hardening

### Multi-Factor Authentication (MFA / 2FA)
- Implemented using Time-Based One-Time Password algorithm (RFC 6238 / TOTP).
- Base32 secret generated via `pyotp.random_base32()`.
- Provisioning URI generated for Google Authenticator, Authy, and 1Password (`otpauth://totp/PayPath:...`).
- Enforces a 1-step window tolerance for clock skew.
- MFA challenge required on login when `user.mfa_enabled = true`.

### Secure Password Reset Flow
- Unpredictable 32-byte cryptographic entropy (`secrets.token_urlsafe(32)`).
- Token stored as a SHA-256 hash in PostgreSQL (`users.password_reset_token`). Raw token is never persisted in plaintext.
- Strict 1-hour expiration timestamp (`users.password_reset_expires`).
- Single-use token: token is erased immediately upon successful password update.
- Generic response message on password reset requests to prevent user enumeration attacks.

### Token Revocation & JTI Blacklisting
- Every issued JWT contains a unique `jti` (JWT ID) and `iat` (issued-at) timestamp.
- Immediate logout revokes the `jti` into the backend revocation registry.
- Deactivated accounts (`is_active = false`) are rejected at the dependency layer (`get_current_user`).

### Role-Based Access Control (RBAC) Matrix
| Resource / Action | USER | MERCHANT_USER | MERCHANT_ADMIN | PLATFORM_ADMIN |
| :--- | :---: | :---: | :---: | :---: |
| View Personal Transactions | ✅ | ✅ | ✅ | ✅ |
| Declare Purchase Intent | ✅ | ❌ | ❌ | ✅ |
| Approve Reclaim Settlement | ✅ | ❌ | ✅ | ✅ |
| Update Merchant Policies | ❌ | ❌ | ✅ | ✅ |
| Dispatch PayPal Refunds | ❌ | ❌ | ✅ | ✅ |
| View System Audit Logs | ❌ | ❌ | ❌ | ✅ |

---

## 3. Financial Safety & Idempotency
- **Idempotency Vault:** Every mutation endpoint requires `X-Idempotency-Key`. PayPath stores `idempotency_key` along with hashed request parameters and response payloads in `payment_actions`. Replayed requests return the exact previous response without hitting PayPal twice.
- **Amount Boundary Enforcement:** Refund amounts cannot be negative or exceed `captured_amount - sum(previous_refunds)`.
- **Approval Gateways:** Financial mutations exceeding policy thresholds (e.g. >$50.00) strictly transition to `AWAITING_APPROVAL` and cannot execute until an authorized user provides authenticated approval.

---

## 4. File Upload Security
- **Magic Byte Inspection:** Inspects binary headers before saving (`JPEG`: `\xff\xd8\xff`, `PNG`: `\x89PNG`, `WEBP`: `RIFF`, `PDF`: `%PDF`). Disguised executables (`.sh`, `.exe`, `.php`) are rejected with `415 Unsupported Media Type`.
- **Size Limitation:** Hard ceiling enforced at 10 MB per file.
- **Filename Sanitization:** Strips directory traversal sequences (`../`, `..\`), null bytes (`\x00`), and non-alphanumeric characters.
- **Isolated Target Directory:** Files are assigned random UUID prefixes and written strictly inside designated upload storage paths.

---

## 5. AI & Prompt Injection Defenses
- Untrusted text (user descriptions, OCR extractions, policy documents) is wrapped in isolation tags:
  `<UNTRUSTED_EXTERNAL_DOCUMENT>...</UNTRUSTED_EXTERNAL_DOCUMENT>`
- Strict system prompt rules instruct models that text within untrusted blocks cannot invoke tools or modify permissions.
- All agent responses must conform to strict Pydantic JSON schemas.
