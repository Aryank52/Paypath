import base64
import zlib
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from urllib.parse import urlparse
import httpx
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

from app.core.config import settings
from app.core.observability import logger
from app.paycore.client import paypal_client

# In-memory certificate cache: {cert_url: (x509_certificate, fetched_at_timestamp)}
_CERT_CACHE: Dict[str, Tuple[x509.Certificate, float]] = {}
_CERT_CACHE_TTL = 86400.0  # 24 hours

# In-memory test certificate registry for local test suites
_TEST_CERT_REGISTRY: Dict[str, x509.Certificate] = {}

class PayPalWebhookVerificationError(Exception):
    """Raised when webhook signature verification fails."""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class PayPalWebhookVerifier:
    """
    Cryptographic verification engine for PayPal Webhooks.
    Supports:
    1. Direct cryptographic self-verification using PayPal's X.509 certificate & RSA signature.
    2. URL validation to neutralize SSRF & certificate spoofing.
    3. Transmission timestamp validation for replay protection.
    4. Fallback to PayPal's official verify-webhook-signature API when connected.
    5. Test suite certificate generation & verification.
    """

    TRUSTED_HOST_REGEX = re.compile(
        r"^https://api(-m)?\.(sandbox\.)?paypal\.com/v1/notifications/certs/[A-Za-z0-9_-]+$",
        re.IGNORECASE
    )

    @classmethod
    def register_test_cert(cls, cert_url: str, cert: x509.Certificate) -> None:
        """Allows test fixtures to register local certificates for testing."""
        _TEST_CERT_REGISTRY[cert_url] = cert

    @classmethod
    def validate_headers(
        cls,
        auth_algo: Optional[str],
        cert_url: Optional[str],
        transmission_id: Optional[str],
        transmission_sig: Optional[str],
        transmission_time: Optional[str],
    ) -> None:
        """Validates presence of all 5 required PayPal webhook authentication headers."""
        missing = []
        if not auth_algo:
            missing.append("PAYPAL-AUTH-ALGO")
        if not cert_url:
            missing.append("PAYPAL-CERT-URL")
        if not transmission_id:
            missing.append("PAYPAL-TRANSMISSION-ID")
        if not transmission_sig:
            missing.append("PAYPAL-TRANSMISSION-SIG")
        if not transmission_time:
            missing.append("PAYPAL-TRANSMISSION-TIME")

        if missing:
            raise PayPalWebhookVerificationError(
                f"Missing required PayPal webhook headers: {', '.join(missing)}",
                status_code=400
            )

    @classmethod
    def validate_cert_url(cls, cert_url: str) -> None:
        """
        Validates that PAYPAL-CERT-URL belongs strictly to trusted PayPal notification certificate domains.
        Neutralizes Server-Side Request Forgery (SSRF) and rogue certificate injection.
        """
        parsed = urlparse(cert_url)
        if parsed.scheme.lower() != "https":
            raise PayPalWebhookVerificationError(
                f"Invalid certificate URL scheme: {parsed.scheme}. Must be https.",
                status_code=400
            )

        # Check PayPal official domain pattern
        domain = parsed.hostname or ""
        valid_domains = [
            "api-m.sandbox.paypal.com",
            "api.sandbox.paypal.com",
            "api-m.paypal.com",
            "api.paypal.com",
        ]
        is_paypal_domain = domain in valid_domains or domain.endswith(".paypal.com")
        path_valid = parsed.path.startswith("/v1/notifications/certs/")

        if not (is_paypal_domain and path_valid):
            raise PayPalWebhookVerificationError(
                f"Untrusted certificate URL host or path: {cert_url}. Must be hosted on paypal.com.",
                status_code=400
            )

    @classmethod
    def validate_timestamp(cls, transmission_time_str: str, max_age_seconds: int = 1800) -> None:
        """
        Validates transmission timestamp to prevent replay attacks.
        Default window: 30 minutes (1800s).
        """
        try:
            # Handle ISO formats like 2026-11-10T22:00:00Z or with microseconds
            time_str = transmission_time_str.replace("Z", "+00:00")
            tx_time = datetime.fromisoformat(time_str)
            now = datetime.now(timezone.utc)
            delta = abs((now - tx_time).total_seconds())

            if delta > max_age_seconds:
                # In test mode, allow older timestamps if specified
                if settings.APP_ENV == "test" and getattr(settings, "TEST_IGNORE_WEBHOOK_TIMESTAMP", False):
                    return
                raise PayPalWebhookVerificationError(
                    f"Webhook timestamp expired or out of bounds (age: {delta:.0f}s, max: {max_age_seconds}s).",
                    status_code=401
                )
        except PayPalWebhookVerificationError:
            raise
        except Exception as e:
            raise PayPalWebhookVerificationError(
                f"Malformed transmission timestamp format: {transmission_time_str} ({e})",
                status_code=400
            )

    @classmethod
    async def fetch_certificate(cls, cert_url: str) -> x509.Certificate:
        """Fetches and caches the X.509 certificate from PayPal or test registry."""
        if cert_url in _TEST_CERT_REGISTRY:
            return _TEST_CERT_REGISTRY[cert_url]

        now = time.time()
        if cert_url in _CERT_CACHE:
            cert, fetched_at = _CERT_CACHE[cert_url]
            if now - fetched_at < _CERT_CACHE_TTL:
                return cert

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(cert_url)
                res.raise_for_status()
                cert_bytes = res.content
                cert = x509.load_pem_x509_certificate(cert_bytes)
                _CERT_CACHE[cert_url] = (cert, now)
                return cert
        except Exception as e:
            logger.error(f"Failed to fetch PayPal webhook certificate from {cert_url}: {e}")
            raise PayPalWebhookVerificationError(
                f"Unable to download PayPal certificate from {cert_url}: {e}",
                status_code=401
            )

    @classmethod
    async def verify_signature(
        cls,
        raw_body: bytes,
        auth_algo: str,
        cert_url: str,
        transmission_id: str,
        transmission_sig: str,
        transmission_time: str,
        webhook_id: Optional[str] = None
    ) -> bool:
        """
        Cryptographically verifies the PayPal webhook signature against the raw request body.
        Expected signed string format:
        <transmission_id>|<transmission_time>|<webhook_id>|<crc32(raw_body)>
        """
        active_webhook_id = webhook_id or getattr(settings, "PAYPAL_WEBHOOK_ID", "") or ""
        
        # 1. Compute CRC32 of exact raw payload bytes
        crc32_val = zlib.crc32(raw_body) & 0xFFFFFFFF
        message_to_verify = f"{transmission_id}|{transmission_time}|{active_webhook_id}|{crc32_val}"

        # 2. Decode signature from base64
        try:
            sig_bytes = base64.b64decode(transmission_sig)
        except Exception:
            raise PayPalWebhookVerificationError("Invalid base64 encoding in PAYPAL-TRANSMISSION-SIG", status_code=401)

        # 3. Retrieve certificate and extract RSA public key
        cert = await cls.fetch_certificate(cert_url)
        public_key = cert.public_key()

        # 4. Perform RSA signature verification
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise PayPalWebhookVerificationError("Certificate public key is not an RSA public key", status_code=401)

        hash_algorithm = hashes.SHA256()
        if "sha1" in auth_algo.lower():
            hash_algorithm = hashes.SHA1()

        try:
            public_key.verify(
                sig_bytes,
                message_to_verify.encode("utf-8"),
                padding.PKCS1v15(),
                hash_algorithm
            )
            logger.info(f"PayPal webhook signature successfully verified for transmission {transmission_id}")
            return True
        except InvalidSignature:
            logger.warning(f"PayPal webhook signature verification failed for transmission {transmission_id}")
            raise PayPalWebhookVerificationError("Invalid PayPal webhook cryptographic signature", status_code=401)
        except Exception as e:
            logger.error(f"Error during signature verification: {e}")
            raise PayPalWebhookVerificationError(f"Signature verification error: {e}", status_code=401)

    @classmethod
    async def verify_via_api(
        cls,
        auth_algo: str,
        cert_url: str,
        transmission_id: str,
        transmission_sig: str,
        transmission_time: str,
        body_json: Dict[str, Any],
        webhook_id: Optional[str] = None
    ) -> bool:
        """Secondary verification via PayPal's verify-webhook-signature API when connected."""
        if not paypal_client.is_configured:
            return False

        active_webhook_id = webhook_id or getattr(settings, "PAYPAL_WEBHOOK_ID", "")
        if not active_webhook_id:
            return False

        try:
            token = await paypal_client.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "auth_algo": auth_algo,
                "cert_url": cert_url,
                "transmission_id": transmission_id,
                "transmission_sig": transmission_sig,
                "transmission_time": transmission_time,
                "webhook_id": active_webhook_id,
                "webhook_event": body_json
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    f"{paypal_client.base_url}/v1/notifications/verify-webhook-signature",
                    headers=headers,
                    json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    status_str = data.get("verification_status")
                    return status_str == "SUCCESS"
        except Exception as e:
            logger.warning(f"PayPal API verify-webhook-signature failed: {e}")
        return False

# Standalone helper for generating test webhook payloads and cryptographic signatures
def create_test_webhook_signed_payload(
    body_json: Dict[str, Any],
    webhook_id: str = "WH-TEST-WEBHOOK-ID",
    transmission_id: Optional[str] = None,
    transmission_time: Optional[str] = None,
    private_key: Optional[rsa.RSAPrivateKey] = None,
    cert_url: str = "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-TEST-KEY"
) -> Tuple[bytes, Dict[str, str]]:
    """
    Generates a cryptographically signed PayPal webhook payload with real RSA PKCS#1 v1.5 signature
    and matching in-memory certificate for test fixtures.
    """
    import json
    from datetime import datetime, timezone

    if private_key is None:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

    # Generate self-signed certificate for the private key
    public_key = private_key.public_key()
    subject = issuer = x509.Name([
        x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "PayPal, Inc."),
        x509.NameAttribute(x509.NameOID.COMMON_NAME, "api.sandbox.paypal.com"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc).replace(year=2030))
        .sign(private_key, hashes.SHA256())
    )

    # Register in test registry
    PayPalWebhookVerifier.register_test_cert(cert_url, cert)

    raw_body = json.dumps(body_json, separators=(',', ':')).encode('utf-8')
    tx_id = transmission_id or f"txid_{int(time.time())}_{zlib.crc32(raw_body)}"
    tx_time = transmission_time or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    crc32_val = zlib.crc32(raw_body) & 0xFFFFFFFF
    message = f"{tx_id}|{tx_time}|{webhook_id}|{crc32_val}"

    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    sig_b64 = base64.b64encode(signature).decode('utf-8')

    headers = {
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-CERT-URL": cert_url,
        "PAYPAL-TRANSMISSION-ID": tx_id,
        "PAYPAL-TRANSMISSION-SIG": sig_b64,
        "PAYPAL-TRANSMISSION-TIME": tx_time,
        "Content-Type": "application/json"
    }
    return raw_body, headers
