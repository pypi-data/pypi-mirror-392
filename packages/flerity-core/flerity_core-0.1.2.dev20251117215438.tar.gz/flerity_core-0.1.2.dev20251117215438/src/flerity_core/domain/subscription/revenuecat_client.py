"""RevenueCat API client for subscription management."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel

from ...utils.errors import BadRequest, DependencyError, InternalError
from ...utils.logging import get_logger
from ...utils.retry import async_retry

logger = get_logger(__name__)


class RevenueCatSubscriberInfo(BaseModel):
    """RevenueCat subscriber information."""
    subscriber: dict[str, Any]
    request_date: str
    request_date_ms: int


class RevenueCatEntitlement(BaseModel):
    """RevenueCat entitlement information."""
    expires_date: str | None = None
    grace_period_expires_date: str | None = None
    product_identifier: str
    purchase_date: str


class RevenueCatWebhookEvent(BaseModel):
    """RevenueCat webhook event model."""
    api_version: str
    event: dict[str, Any]

    @property
    def event_type(self) -> str:
        """Get the event type."""
        return self.event.get("type", "")

    @property
    def app_user_id(self) -> str:
        """Get the app user ID."""
        return self.event.get("app_user_id", "")

    @property
    def original_app_user_id(self) -> str:
        """Get the original app user ID."""
        return self.event.get("original_app_user_id", "")

    @property
    def product_id(self) -> str | None:
        """Get the product ID."""
        return self.event.get("product_id")

    @property
    def period_type(self) -> str | None:
        """Get the period type."""
        return self.event.get("period_type")

    @property
    def purchased_at_ms(self) -> int | None:
        """Get the purchase timestamp in milliseconds."""
        return self.event.get("purchased_at_ms")

    @property
    def expiration_at_ms(self) -> int | None:
        """Get the expiration timestamp in milliseconds."""
        return self.event.get("expiration_at_ms")


class RevenueCatClient:
    """RevenueCat API client for subscription management."""

    def __init__(
        self,
        api_key: str,
        webhook_secret: str | None = None,
        base_url: str = "https://api.revenuecat.com/v1",
        timeout: int = 30,
    ):
        """Initialize RevenueCat client.
        
        Args:
            api_key: RevenueCat API key
            webhook_secret: RevenueCat webhook secret for signature validation
            base_url: RevenueCat API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.base_url = base_url
        self.timeout = timeout

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Flerity/1.0",
            }
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, _exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @async_retry(max_attempts=3)
    async def get_subscriber_info(self, app_user_id: str) -> RevenueCatSubscriberInfo:
        """Get subscriber information from RevenueCat.
        
        Args:
            app_user_id: The app user ID to look up
            
        Returns:
            RevenueCat subscriber information
            
        Raises:
            DependencyError: If RevenueCat API call fails
            BadRequest: If app_user_id is invalid
        """
        if not app_user_id or not app_user_id.strip():
            raise BadRequest("App user ID cannot be empty")

        url = f"{self.base_url}/subscribers/{app_user_id}"

        try:
            logger.info("Fetching subscriber info from RevenueCat", extra={
                "app_user_id": app_user_id,
                "url": url
            })

            response = await self.client.get(url)

            if response.status_code == 404:
                logger.warning("Subscriber not found in RevenueCat", extra={
                    "app_user_id": app_user_id
                })
                # Return empty subscriber info for non-existent users
                return RevenueCatSubscriberInfo(
                    subscriber={},
                    request_date=datetime.utcnow().isoformat(),
                    request_date_ms=int(datetime.utcnow().timestamp() * 1000)
                )

            response.raise_for_status()
            data = response.json()

            logger.info("Successfully fetched subscriber info", extra={
                "app_user_id": app_user_id,
                "has_entitlements": bool(data.get("subscriber", {}).get("entitlements"))
            })

            return RevenueCatSubscriberInfo(**data)

        except httpx.HTTPStatusError as e:
            logger.error("RevenueCat API HTTP error", extra={
                "app_user_id": app_user_id,
                "status_code": e.response.status_code,
                "response_text": e.response.text
            })
            raise DependencyError(f"RevenueCat API error: {e.response.status_code}")

        except httpx.RequestError as e:
            logger.error("RevenueCat API request error", extra={
                "app_user_id": app_user_id,
                "error": str(e)
            })
            raise DependencyError(f"RevenueCat API request failed: {str(e)}")

        except Exception as e:
            logger.error("Unexpected error fetching subscriber info", extra={
                "app_user_id": app_user_id,
                "error": str(e)
            })
            raise InternalError("Failed to fetch subscriber information")

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate RevenueCat webhook signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Signature from X-RevenueCat-Signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature validation")
            return True

        if not signature:
            logger.warning("No signature provided in webhook request")
            return False

        try:
            # RevenueCat uses HMAC-SHA256 for webhook signatures
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures using constant-time comparison
            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                logger.warning("Invalid webhook signature", extra={
                    "provided_signature": signature[:10] + "...",  # Log only first 10 chars
                    "payload_length": len(payload)
                })

            return is_valid

        except Exception as e:
            logger.error("Error validating webhook signature", extra={
                "error": str(e)
            })
            return False

    def parse_webhook_event(self, payload: bytes) -> RevenueCatWebhookEvent:
        """Parse RevenueCat webhook event from payload.
        
        Args:
            payload: Raw webhook payload bytes
            
        Returns:
            Parsed webhook event
            
        Raises:
            BadRequest: If payload is invalid JSON or missing required fields
        """
        try:
            data = json.loads(payload.decode('utf-8'))
            return RevenueCatWebhookEvent(**data)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in webhook payload", extra={
                "error": str(e),
                "payload_length": len(payload)
            })
            raise BadRequest("Invalid JSON in webhook payload")

        except Exception as e:
            logger.error("Error parsing webhook event", extra={
                "error": str(e),
                "payload_length": len(payload)
            })
            raise BadRequest(f"Invalid webhook event format: {str(e)}")

    async def get_entitlements(self, app_user_id: str) -> dict[str, RevenueCatEntitlement]:
        """Get active entitlements for a subscriber.
        
        Args:
            app_user_id: The app user ID to look up
            
        Returns:
            Dictionary of entitlement identifiers to entitlement info
        """
        subscriber_info = await self.get_subscriber_info(app_user_id)
        entitlements_data = subscriber_info.subscriber.get("entitlements", {})

        entitlements = {}
        for entitlement_id, entitlement_data in entitlements_data.items():
            if entitlement_data.get("expires_date") is None or \
               datetime.fromisoformat(entitlement_data["expires_date"].replace('Z', '+00:00')) > datetime.utcnow():
                entitlements[entitlement_id] = RevenueCatEntitlement(**entitlement_data)

        return entitlements

    async def is_subscriber_active(self, app_user_id: str) -> bool:
        """Check if subscriber has any active entitlements.
        
        Args:
            app_user_id: The app user ID to check
            
        Returns:
            True if subscriber has active entitlements, False otherwise
        """
        try:
            entitlements = await self.get_entitlements(app_user_id)
            return len(entitlements) > 0
        except Exception as e:
            logger.error("Error checking subscriber status", extra={
                "app_user_id": app_user_id,
                "error": str(e)
            })
            return False


# Factory function for creating RevenueCat client
def create_revenuecat_client(
    api_key: str,
    webhook_secret: str | None = None,
    base_url: str = "https://api.revenuecat.com/v1",
    timeout: int = 30
) -> RevenueCatClient:
    """Create a RevenueCat client instance.
    
    Args:
        api_key: RevenueCat API key
        webhook_secret: RevenueCat webhook secret
        base_url: RevenueCat API base URL
        timeout: Request timeout in seconds
        
    Returns:
        Configured RevenueCat client
    """
    return RevenueCatClient(
        api_key=api_key,
        webhook_secret=webhook_secret,
        base_url=base_url,
        timeout=timeout
    )


def create_revenuecat_client_from_config() -> RevenueCatClient | None:
    """Create a RevenueCat client from configuration.
    
    Returns:
        Configured RevenueCat client or None if not configured
    """
    from .config import get_subscription_config

    config = get_subscription_config()

    if not config.is_revenuecat_configured():
        logger.warning("RevenueCat not configured, client creation skipped")
        return None

    return RevenueCatClient(
        api_key=config.revenuecat_api_key,
        webhook_secret=config.revenuecat_webhook_secret,
        base_url=config.revenuecat_base_url,
        timeout=config.revenuecat_timeout
    )
