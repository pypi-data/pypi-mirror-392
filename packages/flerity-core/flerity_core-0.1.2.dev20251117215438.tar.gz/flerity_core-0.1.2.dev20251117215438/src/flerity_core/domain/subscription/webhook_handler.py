"""RevenueCat webhook event handler for subscription lifecycle management."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...utils.clock import utcnow
from ...utils.errors import BadRequest, ValidationError
from ...utils.logging import get_logger
from ...utils.redis_client import get_redis_client
from ...utils.tracing import trace_async
from .revenuecat_client import RevenueCatClient
from .schemas import RevenueCatWebhookEvent, RevenueCatWebhookEventType
from .service import SubscriptionService

logger = get_logger(__name__)


class RevenueCatWebhookHandler:
    """Handler for RevenueCat webhook events with idempotency and security."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        webhook_secret: str,
        revenuecat_client: RevenueCatClient | None = None
    ):
        """Initialize webhook handler.
        
        Args:
            session_factory: Database session factory
            webhook_secret: RevenueCat webhook secret for signature validation
            revenuecat_client: Optional RevenueCat client for API calls
        """
        self.session_factory = session_factory
        self.webhook_secret = webhook_secret
        self.revenuecat_client = revenuecat_client
        self.redis_client = get_redis_client()

        # Initialize subscription service
        self.subscription_service = SubscriptionService(
            session_factory=session_factory,
            revenuecat_client=revenuecat_client
        )

        # Idempotency configuration
        self.idempotency_ttl = 86400  # 24 hours
        self.idempotency_key_prefix = "revenuecat:webhook:processed:"

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate RevenueCat webhook signature using HMAC-SHA256.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Signature from webhook headers
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("RevenueCat webhook secret not configured, skipping signature validation")
            return True

        if not signature:
            logger.warning("No signature provided in RevenueCat webhook request")
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
                logger.warning("Invalid RevenueCat webhook signature", extra={
                    "provided_signature": signature[:10] + "...",  # Log only first 10 chars
                    "payload_length": len(payload)
                })
            else:
                logger.debug("RevenueCat webhook signature validated successfully")

            return is_valid

        except Exception as e:
            logger.error("Error validating RevenueCat webhook signature", extra={
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

            # Validate required fields
            if 'api_version' not in data:
                raise ValidationError("Missing api_version field")

            if 'event' not in data or not isinstance(data['event'], dict):
                raise ValidationError("Missing or invalid event field")

            event_data = data['event']
            required_event_fields = ['type', 'app_user_id']
            for field in required_event_fields:
                if field not in event_data:
                    raise ValidationError(f"Event missing required field: {field}")

            return RevenueCatWebhookEvent(**data)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in RevenueCat webhook payload", extra={
                "error": str(e),
                "payload_length": len(payload)
            })
            raise BadRequest("Invalid JSON in webhook payload")

        except ValidationError as e:
            logger.error("Invalid RevenueCat webhook event format", extra={
                "error": str(e),
                "payload_length": len(payload)
            })
            raise BadRequest(f"Invalid webhook event format: {str(e)}")

        except Exception as e:
            logger.error("Error parsing RevenueCat webhook event", extra={
                "error": str(e),
                "payload_length": len(payload)
            })
            raise BadRequest(f"Failed to parse webhook event: {str(e)}")

    async def is_event_processed(self, event_id: str) -> bool:
        """Check if event has already been processed (idempotency).
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            True if event was already processed, False otherwise
        """
        try:
            cache_key = f"{self.idempotency_key_prefix}{event_id}"
            result = await self.redis_client.get(cache_key)
            return result is not None
        except Exception as e:
            logger.warning("Failed to check event idempotency", extra={
                "event_id": event_id,
                "error": str(e)
            })
            # Default to not processed to avoid blocking legitimate events
            return False

    async def mark_event_processed(self, event_id: str) -> None:
        """Mark event as processed for idempotency.
        
        Args:
            event_id: Unique event identifier
        """
        try:
            cache_key = f"{self.idempotency_key_prefix}{event_id}"
            await self.redis_client.set(
                cache_key,
                utcnow().isoformat(),
                ex=self.idempotency_ttl
            )
        except Exception as e:
            logger.warning("Failed to mark event as processed", extra={
                "event_id": event_id,
                "error": str(e)
            })

    def generate_event_id(self, event: RevenueCatWebhookEvent) -> str:
        """Generate unique event ID for idempotency.
        
        Uses RevenueCat's unique event ID if available, otherwise falls back to hash.
        
        Args:
            event: RevenueCat webhook event
            
        Returns:
            Unique event identifier
        """
        # Use RevenueCat's unique event ID if available (recommended)
        if event.event_id:
            return event.event_id

        # Fallback: Create hash from key event data
        timestamp = event.event_timestamp_ms or int(utcnow().timestamp() * 1000)
        event_type = event.event_type
        app_user_id = event.app_user_id
        transaction_id = event.transaction_id or ""

        event_data = f"{timestamp}:{event_type}:{app_user_id}:{transaction_id}"
        event_hash = hashlib.sha256(event_data.encode()).hexdigest()[:16]

        return f"{event_type}_{app_user_id}_{event_hash}"

    @trace_async
    async def process_webhook_event(self, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Process RevenueCat webhook event with idempotency and error handling.
        
        Args:
            event: Parsed RevenueCat webhook event
            
        Returns:
            Processing result dictionary
            
        Raises:
            BadRequest: If event processing fails
        """
        from ...utils.request_tracking import RequestTracker
        from ...utils.domain_logger import get_domain_logger
        
        domain_logger = get_domain_logger(__name__)
        event_id = self.generate_event_id(event)

        with RequestTracker(operation="process_webhook_event", resource=f"event_{event.event_type}") as tracker:
            try:
                tracking_context = domain_logger.operation_start(
                    operation="process_webhook_event",
                    context={
                        "event_id": event_id,
                        "event_type": event.event_type,
                        "app_user_id": event.app_user_id,
                        "product_id": event.product_id
                    }
                )

                logger.info("Processing RevenueCat webhook event", extra={
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "app_user_id": event.app_user_id,
                    "product_id": event.product_id
                })

                # Check idempotency
                if await self.is_event_processed(event_id):
                    logger.info("RevenueCat webhook event already processed", extra={
                        "event_id": event_id,
                        "event_type": event.event_type,
                        "app_user_id": event.app_user_id
                    })
                    
                    result = {
                        "status": "duplicate",
                        "event_id": event_id,
                        "message": "Event already processed"
                    }
                    
                    tracker.log_success(result_id=event_id)
                    tracking_context = domain_logger.operation_start("process_webhook_event")

                    domain_logger.operation_success(tracking_context,
                        context={
                            "event_id": event_id,
                            "status": "duplicate",
                            "event_type": event.event_type
                        }
                    )
                    domain_logger.business_event(
                        event="webhook_event_duplicate",
                        context={
                            "event_id": event_id,
                            "event_type": event.event_type,
                            "app_user_id": event.app_user_id
                        }
                    )
                    
                    return result

                # Validate user ID format
                try:
                    user_id = UUID(event.app_user_id)
                except ValueError:
                    logger.error("Invalid user ID format in webhook event", extra={
                        "event_id": event_id,
                        "app_user_id": event.app_user_id
                    })
                    raise BadRequest(f"Invalid user ID format: {event.app_user_id}")

                # Process event based on type
                result = await self._handle_event_by_type(user_id, event)

                # Mark event as processed
                await self.mark_event_processed(event_id)

                tracker.log_success(result_id=event_id)
                tracking_context = domain_logger.operation_start("process_webhook_event")

                domain_logger.operation_success(tracking_context,
                    context={
                        "event_id": event_id,
                        "event_type": event.event_type,
                        "user_id": str(user_id),
                        "action": result.get("action"),
                        "status": "processed"
                    }
                )
                domain_logger.business_event(
                    event="webhook_event_processed",
                    context={
                        "event_id": event_id,
                        "event_type": event.event_type,
                        "user_id": str(user_id),
                        "action": result.get("action")
                    }
                )

                logger.info("RevenueCat webhook event processed successfully", extra={
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "user_id": str(user_id),
                    "result": result
                })

                return {
                    "status": "processed",
                    "event_id": event_id,
                    "message": "Event processed successfully",
                    "result": result
                }

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "app_user_id": event.app_user_id
                })
                tracking_context = domain_logger.operation_start("process_webhook_event")

                domain_logger.operation_error(tracking_context,
                    error=e,
                    context={
                        "event_id": event_id,
                        "event_type": event.event_type,
                        "app_user_id": event.app_user_id,
                        "error_id": error_id
                    }
                )
                
                logger.error("Failed to process RevenueCat webhook event", extra={
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "app_user_id": event.app_user_id,
                    "error": str(e)
                })
                raise BadRequest(f"Failed to process webhook event: {str(e)}")

    async def _handle_event_by_type(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle webhook event based on its type.
        
        Args:
            user_id: User UUID
            event: RevenueCat webhook event
            
        Returns:
            Event processing result
        """
        event_type = event.event_type

        # Subscription lifecycle events
        if event_type == RevenueCatWebhookEventType.INITIAL_PURCHASE:
            return await self._handle_initial_purchase(user_id, event)
        elif event_type == RevenueCatWebhookEventType.RENEWAL:
            return await self._handle_renewal(user_id, event)
        elif event_type == RevenueCatWebhookEventType.NON_RENEWING_PURCHASE:
            return await self._handle_non_renewing_purchase(user_id, event)

        # Cancellation and reactivation
        elif event_type == RevenueCatWebhookEventType.CANCELLATION:
            return await self._handle_cancellation(user_id, event)
        elif event_type == RevenueCatWebhookEventType.UNCANCELLATION:
            return await self._handle_uncancellation(user_id, event)
        elif event_type == RevenueCatWebhookEventType.EXPIRATION:
            return await self._handle_expiration(user_id, event)

        # Billing and payment
        elif event_type == RevenueCatWebhookEventType.BILLING_ISSUE:
            return await self._handle_billing_issue(user_id, event)
        elif event_type == RevenueCatWebhookEventType.PRODUCT_CHANGE:
            return await self._handle_product_change(user_id, event)

        # Refunds (critical for revenue tracking)
        elif event_type == RevenueCatWebhookEventType.REFUND:
            return await self._handle_refund(user_id, event)
        elif event_type == RevenueCatWebhookEventType.REFUND_REVERSED:
            return await self._handle_refund_reversed(user_id, event)

        # Android-specific subscription management
        elif event_type == RevenueCatWebhookEventType.SUBSCRIPTION_PAUSED:
            return await self._handle_subscription_paused(user_id, event)
        elif event_type == RevenueCatWebhookEventType.SUBSCRIPTION_EXTENDED:
            return await self._handle_subscription_extended(user_id, event)

        # Transfer and test
        elif event_type == RevenueCatWebhookEventType.TRANSFER:
            return await self._handle_transfer(user_id, event)
        elif event_type == RevenueCatWebhookEventType.TEST:
            return await self._handle_test_event(user_id, event)

        else:
            logger.warning("Unhandled RevenueCat webhook event type", extra={
                "event_type": event_type,
                "user_id": str(user_id),
                "store": event.store
            })
            return {
                "action": "ignored",
                "reason": f"Unhandled event type: {event_type}"
            }

    async def _handle_initial_purchase(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle initial purchase event (trial to paid upgrade)."""
        logger.info("Handling initial purchase event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id
        })

        # Upgrade trial to paid subscription
        result = await self.subscription_service.upgrade_trial_to_paid(
            user_id=user_id,
            revenuecat_subscriber_id=event.original_app_user_id
        )

        return {
            "action": "trial_upgraded_to_paid",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "product_id": event.product_id
        }

    async def _handle_renewal(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle renewal event for paid subscriptions."""
        logger.info("Handling renewal event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id
        })

        # Sync with RevenueCat to get latest subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_renewed",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None
        }

    async def _handle_non_renewing_purchase(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle non-renewing purchase event (one-time purchase)."""
        logger.info("Handling non-renewing purchase event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "non_renewing_purchase",
            "subscription_tier": result.subscription_tier.value,
            "product_id": event.product_id,
            "store": event.store
        }

    async def _handle_cancellation(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle cancellation event."""
        logger.info("Handling cancellation event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_cancelled",
            "subscription_tier": result.subscription_tier.value,
            "will_renew": result.will_renew,
            "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None
        }

    async def _handle_uncancellation(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle uncancellation event (reactivation of cancelled subscription)."""
        logger.info("Handling uncancellation event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_reactivated",
            "subscription_tier": result.subscription_tier.value,
            "will_renew": result.will_renew,
            "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None
        }

    async def _handle_expiration(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle expiration event (downgrade to trial)."""
        logger.info("Handling expiration event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status (should downgrade to trial)
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_expired",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "trial_end_date": result.trial_end_date.isoformat() if result.trial_end_date else None
        }

    async def _handle_refund(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle refund event (CRITICAL: user got money back, revoke access)."""
        logger.warning("Handling refund event - revoking access", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "transaction_id": event.transaction_id,
            "store": event.store,
            "price": event.price_in_purchased_currency,
            "currency": event.currency
        })

        # Sync with RevenueCat to revoke entitlements
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "refund_processed",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "transaction_id": event.transaction_id,
            "refund_amount": event.price_in_purchased_currency
        }

    async def _handle_refund_reversed(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle refund reversal event (refund was cancelled, restore access)."""
        logger.info("Handling refund reversal event - restoring access", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "transaction_id": event.transaction_id,
            "store": event.store
        })

        # Sync with RevenueCat to restore entitlements
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "refund_reversed",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "transaction_id": event.transaction_id
        }

    async def _handle_subscription_paused(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle subscription paused event (Android Play Store only)."""
        logger.info("Handling subscription paused event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_paused",
            "subscription_tier": result.subscription_tier.value,
            "store": event.store
        }

    async def _handle_subscription_extended(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle subscription extended event (grace period or extension)."""
        logger.info("Handling subscription extended event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "new_expiration": event.expiration_at_ms,
            "store": event.store
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_extended",
            "subscription_tier": result.subscription_tier.value,
            "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None
        }

    async def _handle_transfer(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle transfer event (subscription transferred between users)."""
        logger.info("Handling transfer event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id,
            "original_app_user_id": event.original_app_user_id
        })

        # Sync with RevenueCat to update subscription status
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "subscription_transferred",
            "subscription_tier": result.subscription_tier.value,
            "from_user": event.original_app_user_id
        }

    async def _handle_test_event(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle test event from RevenueCat dashboard."""
        logger.info("Handling test event", extra={
            "user_id": str(user_id),
            "event_type": event.event_type,
            "store": event.store
        })

        return {
            "action": "test_event_received",
            "message": "Test event processed successfully",
            "store": event.store
        }

    async def _handle_billing_issue(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle billing issue event."""
        logger.info("Handling billing issue event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id
        })

        # Update subscription to mark billing issue
        from .schemas import SubscriptionStatusUpdate
        result = await self.subscription_service.update_subscription_status(
            user_id=user_id,
            data=SubscriptionStatusUpdate(billing_issue=True)
        )

        return {
            "action": "billing_issue_flagged",
            "billing_issue": True,
            "subscription_tier": result.subscription_tier.value if result else "unknown"
        }

    async def _handle_product_change(self, user_id: UUID, event: RevenueCatWebhookEvent) -> dict[str, Any]:
        """Handle product change event."""
        logger.info("Handling product change event", extra={
            "user_id": str(user_id),
            "product_id": event.product_id
        })

        # Sync with RevenueCat to get updated subscription info
        result = await self.subscription_service.sync_with_revenuecat(user_id)

        return {
            "action": "product_changed",
            "subscription_tier": result.subscription_tier.value,
            "entitlement": result.entitlement,
            "product_id": event.product_id
        }


def create_revenuecat_webhook_handler(
    session_factory: async_sessionmaker[AsyncSession],
    webhook_secret: str,
    revenuecat_client: RevenueCatClient | None = None
) -> RevenueCatWebhookHandler:
    """Factory function for RevenueCat webhook handler.
    
    Args:
        session_factory: Database session factory
        webhook_secret: RevenueCat webhook secret
        revenuecat_client: Optional RevenueCat client
        
    Returns:
        Configured webhook handler
    """
    return RevenueCatWebhookHandler(
        session_factory=session_factory,
        webhook_secret=webhook_secret,
        revenuecat_client=revenuecat_client
    )
