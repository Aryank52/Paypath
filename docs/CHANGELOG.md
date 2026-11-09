# PayPath Changelog

All notable changes to the PayPath platform are documented in this file.

## [1.0.0] — 2026-11-09
### Added
- **PostgreSQL 16 Authoritative Migration**: Full transition to PostgreSQL 16 with async SQLAlchemy 2.0 and `asyncpg` connection pooling.
- **Alembic Database Migrations**: Async Alembic initialization with initial schema revision `941e4676f903`.
- **Two-Factor Authentication (MFA)**: TOTP generator, QR code provisioning URI, and verification challenge via `pyotp`.
- **Password Reset Flow**: Cryptographically secure 32-byte reset tokens with SHA-256 storage and 1-hour expiration.
- **File Upload Hardening**: Added magic-byte inspection (JPEG, PNG, WEBP, PDF), 10 MB size limit, and path traversal sanitization.
- **Intent-Aware Prefetching**: AG Grid row hover prefetching in `TransactionExplorer` to make lifecycle inspection instantaneous.
- **Persona Switcher**: Real-time role toggle between Shopper and Merchant Admin in top navigation.
- **Documentation Suite**: Added 17 required engineering specifications under `docs/`.

### Fixed
- **Localhost Connectivity**: Resolved port binding and background daemon orchestration for FastAPI (:8000) and Vite (:5173).
- **SQLite Fallback Removal**: Enforced PostgreSQL 16 as the system of record for development and production.
- **Event Loop Disconnection in Tests**: Added NullPool connection configuration and isolated test database fixtures.
- **Foreign Key Seeding Order**: Fixed startup lifecycle ordering to guarantee parent entity commitment before child table insertions.
- **Passlib Bcrypt Compatibility**: Migrated to native bcrypt module to prevent `__about__` attribute exceptions.

### Changed
- Refactored `deps.py` to support `demo@paypath.ai` and `demo@paypath.finance` demo accounts.
- Updated `backend/requirements.txt` with pinned `pyotp>=2.9.0` and `email-validator>=2.2.0`.

