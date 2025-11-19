"""Cryptographic utilities for Flerity backend services.

Provides safe, deterministic utilities for hashing and message authentication
using only Python standard library. All functions are side-effect free.

Security Notes:
- Never roll your own crypto beyond these basic primitives
- Use constant_time_compare for all equality checks on secrets
- Keys/secrets must come from secure storage (AWS Secrets Manager)
- Base64url encoding without padding is safer for headers/URLs
- Do not auto-strip inputs; callers must normalize upstream
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Union

# Type aliases for cleaner signatures
BytesLike = Union[bytes, bytearray]
StrOrBytes = Union[str, bytes, bytearray]


def _to_bytes(value: StrOrBytes) -> bytes:
    """Convert str/bytes/bytearray to bytes.
    
    Args:
        value: Input to convert
        
    Returns:
        bytes representation
        
    Raises:
        TypeError: If value is not str, bytes, or bytearray
    """
    if isinstance(value, str):
        return value.encode('utf-8')
    elif isinstance(value, bytes):
        return value
    elif isinstance(value, bytearray):
        return bytes(value)
    else:
        raise TypeError(f"Expected str, bytes, or bytearray, got {type(value)}")


def _b64url_encode(raw: bytes) -> str:
    """Encode bytes as URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def _b64url_decode(s: str) -> bytes:
    """Decode URL-safe base64 string, tolerant of missing padding.
    
    Args:
        s: Base64url string to decode
        
    Returns:
        Decoded bytes
        
    Raises:
        ValueError: If input is invalid base64
    """
    # Add missing padding
    padding = (-len(s)) % 4
    s_padded = s + ('=' * padding)
    return base64.urlsafe_b64decode(s_padded)


def sha256_hex(data: StrOrBytes, *, salt: StrOrBytes | None = None) -> str:
    """Compute SHA-256 hash as lowercase hex string.
    
    Args:
        data: Data to hash
        salt: Optional salt prepended to data
        
    Returns:
        Lowercase hex SHA-256 digest
    """
    hasher = hashlib.sha256()
    if salt is not None:
        hasher.update(_to_bytes(salt))
    hasher.update(_to_bytes(data))
    return hasher.hexdigest()


def sha256_bytes(data: StrOrBytes, *, salt: StrOrBytes | None = None) -> bytes:
    """Compute SHA-256 hash as raw bytes.
    
    Args:
        data: Data to hash
        salt: Optional salt prepended to data
        
    Returns:
        32-byte SHA-256 digest
    """
    hasher = hashlib.sha256()
    if salt is not None:
        hasher.update(_to_bytes(salt))
    hasher.update(_to_bytes(data))
    return hasher.digest()


def sha256_b64url(data: StrOrBytes, *, salt: StrOrBytes | None = None) -> str:
    """Compute SHA-256 hash as URL-safe base64 without padding.
    
    Args:
        data: Data to hash
        salt: Optional salt prepended to data
        
    Returns:
        SHA-256 hash as URL-safe base64 string (no padding)
    """
    return _b64url_encode(sha256_bytes(data, salt=salt))


def hmac_sha256_hex(key: StrOrBytes, data: StrOrBytes) -> str:
    """Compute HMAC-SHA256 as lowercase hex string.
    
    Args:
        key: HMAC key
        data: Data to authenticate
        
    Returns:
        Lowercase hex HMAC-SHA256
    """
    return hmac.new(_to_bytes(key), _to_bytes(data), hashlib.sha256).hexdigest()


def hmac_sha256_bytes(key: StrOrBytes, data: StrOrBytes) -> bytes:
    """Compute HMAC-SHA256 as raw bytes.
    
    Args:
        key: HMAC key
        data: Data to authenticate
        
    Returns:
        32-byte HMAC-SHA256
    """
    return hmac.new(_to_bytes(key), _to_bytes(data), hashlib.sha256).digest()


def hash_sensitive_data(data: str, salt: str = "") -> str:
    """Hash sensitive data with optional salt."""
    return sha256_hex(data, salt=salt)


def hmac_sha256_b64url(key: StrOrBytes, data: StrOrBytes) -> str:
    """Compute HMAC-SHA256 as URL-safe base64 without padding.
    
    Args:
        key: HMAC key
        data: Data to authenticate
        
    Returns:
        URL-safe base64 HMAC-SHA256 (no padding)
    """
    mac_bytes = hmac_sha256_bytes(key, data)
    return _b64url_encode(mac_bytes)


def constant_time_compare(a: StrOrBytes, b: StrOrBytes) -> bool:
    """Compare two values in constant time to prevent timing attacks.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        True if values are equal, False otherwise
    """
    a_bytes = _to_bytes(a)
    b_bytes = _to_bytes(b)
    return hmac.compare_digest(a_bytes, b_bytes)


def secure_random_bytes(nbytes: int = 32) -> bytes:
    """Generate cryptographically strong random bytes.
    
    Args:
        nbytes: Number of bytes to generate
        
    Returns:
        Random bytes
    """
    return secrets.token_bytes(nbytes)


def random_token_b64url(nbytes: int = 32) -> str:
    """Generate random token as URL-safe base64 without padding.
    
    Args:
        nbytes: Number of random bytes to generate
        
    Returns:
        URL-safe base64 token (no padding)
    """
    return _b64url_encode(secure_random_bytes(nbytes))


def sign_message(key: StrOrBytes, message: StrOrBytes) -> str:
    """Sign message with HMAC-SHA256, returning URL-safe base64 signature.
    
    Args:
        key: Signing key
        message: Message to sign
        
    Returns:
        URL-safe base64 signature (no padding)
    """
    return hmac_sha256_b64url(key, message)


def verify_signature(key: StrOrBytes, message: StrOrBytes, signature_b64url: str) -> bool:
    """Verify HMAC-SHA256 signature in constant time.
    
    Args:
        key: Signing key
        message: Original message
        signature_b64url: URL-safe base64 signature to verify
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = sign_message(key, message)
    return constant_time_compare(expected_signature, signature_b64url)
