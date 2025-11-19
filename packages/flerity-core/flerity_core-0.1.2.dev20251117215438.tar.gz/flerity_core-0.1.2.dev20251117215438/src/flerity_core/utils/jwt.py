"""JWT token utilities for authentication."""

import os
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from cryptography.hazmat.primitives import serialization

from ..domain.auth.schemas import TokenClaims, TokenType
from .clock import utcnow
from .logging import get_logger

logger = get_logger(__name__)

# Use HMAC for testing, RSA for production
_TEST_SECRET = "test-secret-key-for-jwt-testing-only"

def _get_jwt_config() -> tuple[str, str]:
    """Get JWT algorithm and key/secret."""
    # Use HMAC for testing/development
    if os.getenv("ENV") in ("test", "dev") or "pytest" in os.environ.get("_", ""):
        return "HS256", _TEST_SECRET

    # Use RSA for production
    private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH")
    if private_key_path and os.path.exists(private_key_path):
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        return "RS256", private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

    # Fallback to HMAC if RSA key not available
    logger.warning("RSA private key not found, falling back to HMAC")
    return "HS256", os.getenv("JWT_SECRET", "production-secret-key")

def generate_access_token(user_id: UUID, email: str, expires_minutes: int = 15, device_id: str | None = None) -> str:
    """Generate JWT access token."""
    algorithm, secret = _get_jwt_config()
    now = utcnow()

    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "jti": str(uuid4()),
        "type": TokenType.access.value,
        "device_id": device_id
    }

    return jwt.encode(payload, secret, algorithm=algorithm)

def validate_token(token: str) -> TokenClaims:
    """Validate and decode JWT token."""
    algorithm, key_material = _get_jwt_config()

    logger.debug("JWT validation", extra={
        "algorithm": algorithm,
        "env": os.getenv("ENV"),
        "token_length": len(token)
    })

    # For RSA, we need the public key for validation
    if algorithm == "RS256":
        public_key_path = os.getenv("JWT_PUBLIC_KEY_PATH")
        if public_key_path and os.path.exists(public_key_path):
            with open(public_key_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
            key_material = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        else:
            logger.error("RSA public key not found for token validation")
            raise ValueError("Public key not available for token validation")

    try:
        payload = jwt.decode(token, key_material, algorithms=[algorithm])
        return TokenClaims(
            sub=UUID(payload["sub"]),
            email=payload["email"],
            iat=payload["iat"],
            exp=payload["exp"],
            jti=payload["jti"],
            type=TokenType(payload.get("type", "access")),
            device_id=payload.get("device_id")
        )
    except jwt.InvalidTokenError as e:
        logger.warning("JWT validation failed", extra={
            "error": str(e),
            "algorithm": algorithm,
            "token_length": len(token)
        })
        raise

def decode_token_unsafe(token: str) -> dict[str, Any]:
    """Decode token without validation (for expired token inspection)."""
    decoded = jwt.decode(token, options={"verify_signature": False})
    return dict(decoded) if decoded else {}
