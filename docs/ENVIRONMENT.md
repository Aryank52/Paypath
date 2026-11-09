# PayPath Environment & Configuration Reference

## Overview
All application parameters are declared through typed Pydantic Settings in `backend/app/core/config.py` and sourced from the root `.env` file.

---

## Configuration Variables

### Core Application
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | string | `"PayPath"` | Display name of the platform. |
| `APP_ENV` | string | `"development"` | Environment: `development`, `test`, `production`. |
| `API_V1_STR` | string | `"/api/v1"` | Route prefix for REST endpoints. |
| `SECRET_KEY` | string | *(random string)* | Cryptographic key for signing JWT tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `1440` | JWT token validity window (minutes). |

### Database & Storage
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | string | `postgresql+asyncpg://...` | Authoritative PostgreSQL connection string. |
| `REDIS_URL` | string | `None` | Optional Redis URL for distributed rate limiting. |

### PayPal Sandbox Integration
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `PAYPAL_CLIENT_ID` | string | *(empty)* | PayPal Sandbox REST App Client ID. |
| `PAYPAL_CLIENT_SECRET` | string | *(empty)* | PayPal Sandbox REST App Secret. |
| `PAYPAL_BASE_URL` | string | `https://api-m.sandbox.paypal.com` | Base URL for PayPal Sandbox API v2. |
| `PAYPAL_WEBHOOK_ID` | string | *(empty)* | Registered PayPal Webhook listener ID. |

### AI Engine (Google Gemini)
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | string | *(empty)* | Google GenAI API key for multi-agent reasoning. |
| `LLM_PROVIDER` | string | `"gemini"` | Active provider: `gemini` or `mock`. |
| `LLM_MODEL` | string | `"gemini-2.5-flash"` | Target LLM model identifier. |

### Feature Flags
| Variable | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `ENABLE_VOICE` | boolean | `true` | Enables Web Speech API voice synthesis & input. |
| `ENABLE_SHOPPING` | boolean | `true` | Activates autonomous shopping assistant. |
| `ENABLE_AGENTIC_PURCHASE`| boolean | `true` | Allows agentic checkout proposals. |
| `ENABLE_RECOVERY` | boolean | `true` | Enables recurring subscription anomaly tracker. |
| `ENABLE_RECLAIM` | boolean | `true` | Enables RECLAIM dispute resolution engine. |
| `ENABLE_MULTI_MERCHANT` | boolean | `true` | Activates multi-tenant merchant portal. |

