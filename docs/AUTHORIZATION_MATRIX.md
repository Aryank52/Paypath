# PayPath Authorization Matrix & Security Access Control Specification

**Document Version:** 1.0.0  
**Status:** Certified & Production Verified  
**Authoritative RBAC Engine:** FastAPI Dependency Injection (`get_current_user`, `require_role`, `verify_merchant_access`)  
**JWT Standard:** HMAC-SHA256 with user ID, role claim, expiration timestamp, and session revocation tracking  

---

## 1. Executive Summary

PayPath implements an authoritative, defense-in-depth Role-Based Access Control (RBAC) and Tenant-Isolation model. Client-side persona switches and frontend state representations are strictly non-authoritative; every single API endpoint validates the cryptographically signed JWT token and cross-checks resource ownership to prevent Insecure Direct Object Reference (IDOR) attacks.

---

## 2. Defined Roles and Permissions

| Role Identifier | Description | Typical Personas | Primary Scope |
| :--- | :--- | :--- | :--- |
| `USER` / `SHOPPER` | Authenticated retail consumer / shopper | Alex Chen (`demo@paypath.finance`), Elena Rostova | Read own transactions, initiate disputes/RECLAIM cases, view own policy matches, upload dispute evidence, update profile |
| `MERCHANT_ADMIN` | Authenticated enterprise merchant representative | Sarah Jenkins (`sarah.jenkins@paypath.finance`) | Manage own merchant profile, define return/dispute policies, view merchant-scoped transactions and dispute claims |
| `PLATFORM_ADMIN` | Global PayPath platform operations / risk lead | Marcus Vance (`marcus.vance@paypath.finance`) | Full administrative oversight: system health, global telemetry, seed triggers, dead-letter queues, merchant onboarding |
| `PUBLIC` / `UNAUTHENTICATED` | Anonymous visitor | New signup / landing visitor | Access health checks, view public landing/docs, log in, register, receive PayPal webhook events (validated by PayPal signature) |

---

## 3. Comprehensive Endpoint Authorization Matrix

### 3.1 Authentication & Profile (`/api/v1/auth`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | `PUBLIC` | Open registration with bcrypt password hashing | Rejects duplicate emails; sets default role `USER` |
| `POST` | `/api/v1/auth/login` | `PUBLIC` | Credential verification + optional MFA TOTP check | Validates active account status; returns signed JWT |
| `GET` | `/api/v1/auth/me` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Returns caller's own profile only |
| `POST` | `/api/v1/auth/mfa/setup` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Sets TOTP secret on caller's account only |
| `POST` | `/api/v1/auth/mfa/verify` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Verifies and activates TOTP for caller's account only |
| `POST` | `/api/v1/auth/logout` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Revokes session token in database revocation list |

### 3.2 Transactions & Ledger (`/api/v1/transactions`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/transactions` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | **Strict Isolation:** `USER` receives only their own records (`user_id == current_user.id`). `MERCHANT_ADMIN` receives only transactions tied to their assigned merchant. `PLATFORM_ADMIN` has global read access. |
| `GET` | `/api/v1/transactions/{id}` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Verified ownership check: Returns 404 or 403 if transaction does not belong to user or merchant. |
| `POST` | `/api/v1/transactions/sync` | `USER`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Triggers sync only for the caller's linked account. |

### 3.3 Post-Purchase Dispute & Resolution (`/api/v1/reclaim`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/reclaim/cases` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Filters cases by caller: Shopper sees their initiated disputes; Merchant Admin sees cases against their merchant. |
| `POST` | `/api/v1/reclaim/cases` | `USER` | `require_role(USER)` | Auto-assigns `user_id = current_user.id`; verifies transaction belongs to caller before opening claim. |
| `GET` | `/api/v1/reclaim/cases/{id}` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Explicit tenant validation: Denies access if caller is neither the case creator nor the target merchant. |
| `POST` | `/api/v1/reclaim/cases/{id}/evidence` | `USER`, `MERCHANT_ADMIN` | `Depends(get_current_user)` | Validates case participation; magic-byte and file size verification enforced. |
| `POST` | `/api/v1/reclaim/cases/{id}/settle` | `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `require_role(MERCHANT_ADMIN, PLATFORM_ADMIN)` | Verifies merchant owns the dispute before executing settlement or refund. |

### 3.4 Merchant Governance & Policy Management (`/api/v1/merchants`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/merchants` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Public directory of active verified merchants. |
| `GET` | `/api/v1/merchants/{id}` | `USER`, `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `Depends(get_current_user)` | Read merchant details, policy summaries, and trust tiers. |
| `POST` | `/api/v1/merchants/{id}/policies` | `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `require_role(MERCHANT_ADMIN, PLATFORM_ADMIN)` | **Strict Multi-Tenant Check:** `MERCHANT_ADMIN` can ONLY mutate policies if `current_user.merchant_id == id`. Unauthorized updates return 403 Forbidden. |
| `PUT` | `/api/v1/merchants/{id}` | `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `require_role(MERCHANT_ADMIN, PLATFORM_ADMIN)` | Enforces merchant assignment guard. |

### 3.5 PayCore & Real-Time PayPal Execution (`/api/v1/paycore`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/paycore/orders` | `USER` | `require_role(USER)` | Initiates PayPal Sandbox order tied strictly to authenticated `current_user.id`. |
| `POST` | `/api/v1/paycore/orders/{id}/capture` | `USER` | `require_role(USER)` | Captures order with idempotency key; independently verifies capture state with PayPal. |
| `POST` | `/api/v1/paycore/refunds` | `MERCHANT_ADMIN`, `PLATFORM_ADMIN` | `require_role(MERCHANT_ADMIN, PLATFORM_ADMIN)` | Enforces payment action lineage and merchant ownership of transaction. |
| `POST` | `/api/v1/paycore/webhooks/paypal` | `PUBLIC` (Webhook Engine) | Signature verification via PayPal API / Public Key | Validates transmission ID, timestamp, HMAC-SHA256 signature, and replay protection cache. |

### 3.6 Platform Administration & Observability (`/api/v1/system`)

| Method | Endpoint | Allowed Roles | Authorization Enforcement | IDOR / Tenant Boundary Guard |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | `PUBLIC` | None | Returns high-level operational status, database connectivity, and version. |
| `GET` | `/api/v1/system/status` | `PLATFORM_ADMIN` | `require_role(PLATFORM_ADMIN)` | Detailed infrastructure diagnostics, connection pool stats, queue depths. |
| `POST` | `/api/v1/system/seed` | `PLATFORM_ADMIN` | `require_role(PLATFORM_ADMIN)` | Controlled seed/repair trigger; prohibited from unauthorized execution in production. |
| `GET` | `/api/v1/system/audit` | `PLATFORM_ADMIN` | `require_role(PLATFORM_ADMIN)` | Immutable financial action and authorization audit trail. |

---

## 4. Verification and Enforcement Guarantee

1. **Non-Authoritative UI:** Toggling personas in the PayPath frontend updates the interface display and triggers an explicit re-authentication request against `/api/v1/auth/login`. If a token lacks the authoritative role claim, the backend rejects the request immediately.
2. **Deterministic Token Invalidation:** When a user logs out, their token jti is placed in the database revocation table. Subsequent API calls with that token return 401 Unauthorized regardless of expiration window.
3. **Database-Enforced Tenant Isolation:** Where applicable, foreign key constraints and SQL queries filter by `user_id` or `merchant_id` at the query builder layer, preventing data leakage even in the event of an application logic anomaly.

