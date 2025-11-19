"""Integration service for managing external provider connections."""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import httpx

# Check httpx version compatibility
try:
    httpx.AsyncClient
    HTTPX_ASYNC_AVAILABLE = True
    HTTPX_CLIENT_CLASS = httpx.AsyncClient
except AttributeError:
    # Fallback to sync Client for older httpx versions
    try:
        httpx.Client
        HTTPX_ASYNC_AVAILABLE = False
        HTTPX_CLIENT_CLASS = httpx.Client
        logger = __import__('logging').getLogger(__name__)
        logger.warning("Using httpx.Client fallback - AsyncClient not available", extra={
            "httpx_version": getattr(httpx, '__version__', 'unknown')
        })
    except AttributeError:
        HTTPX_ASYNC_AVAILABLE = False
        HTTPX_CLIENT_CLASS = None
        logger = __import__('logging').getLogger(__name__)
        logger.error("No httpx client available", extra={
            "httpx_version": getattr(httpx, '__version__', 'unknown'),
            "httpx_attributes": [attr for attr in dir(httpx) if not attr.startswith('_')][:10]
        })

# Check httpx version compatibility
try:
    httpx.AsyncClient
    HTTPX_ASYNC_AVAILABLE = True
except AttributeError:
    HTTPX_ASYNC_AVAILABLE = False
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...config import config
from ...db.uow import async_uow_factory
from ...utils.clock import utcnow
from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest, Conflict, NotFound
from ...utils.logging import get_safe_logger
from ...utils.redis_client import get_redis_client
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async
from .repository import IntegrationRepository, WhatsAppPairingRepository
from .schemas import (
    IntegrationAccountCreate,
    IntegrationAccountOut,
    IntegrationAccountUpdate,
    IntegrationStatus,
    IntegrationType,
    WhatsAppPairingSessionCreate,
    WhatsAppPairingSessionOut,
    integrations_accounts_table,
)

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger(__name__)


class IntegrationService:
    """Service for managing user integrations with external providers."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def get_user_integrations(self, user_id: UUID) -> list[IntegrationAccountOut]:
        """Get user integration status."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = IntegrationRepository(uow.session)
            result: list[IntegrationAccountOut] = await repository.list_by_user(user_id)
            return result

    @trace_async
    async def get_integration(self, user_id: UUID, provider: IntegrationType) -> IntegrationAccountOut | None:
        """Get specific integration by provider."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = IntegrationRepository(uow.session)
            result: IntegrationAccountOut | None = await repository.get_by_user_provider(user_id, provider)
            return result

    @trace_async
    async def create_integration(
        self, user_id: UUID, provider: IntegrationType, external_user_id: str | None = None,
        meta: dict[str, Any] | None = None
    ) -> IntegrationAccountOut:
        """Create new integration."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = IntegrationRepository(uow.session)

                # Check if already exists
                existing = await repository.get_by_user_provider(user_id, provider)
                if existing:
                    raise Conflict(f"Integration {provider} already exists")

                create_data = IntegrationAccountCreate(
                    user_id=user_id,
                    provider=provider,
                    external_user_id=external_user_id,
                    status="connected",
                    meta=meta or {},
                    connected_at=utcnow()
                )

                result: IntegrationAccountOut = await repository.create(create_data)
                return result
        except Conflict:
            raise
        except Exception as e:
            logger.error("Failed to create integration", extra={
                "user_id": str(user_id), "provider": provider, "error": str(e)
            })
            raise BadRequest("Failed to create integration")

    @trace_async
    async def update_integration(
        self, user_id: UUID, provider: IntegrationType,
        status: IntegrationStatus | None = None, meta: dict[str, Any] | None = None
    ) -> IntegrationAccountOut | None:
        """Update integration."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = IntegrationRepository(uow.session)

                update_data = IntegrationAccountUpdate(
                    status=status,
                    meta=meta,
                    external_user_id=""
                )

                result: IntegrationAccountOut | None = await repository.update(user_id, provider, update_data)
                return result
        except Exception as e:
            logger.error("Failed to update integration", extra={
                "user_id": str(user_id), "provider": provider, "error": str(e)
            })
            raise BadRequest("Failed to update integration")

    @trace_async
    async def connect_integration(
        self, user_id: UUID, provider: IntegrationType,
        external_user_id: str, meta: dict[str, Any] | None = None
    ) -> IntegrationAccountOut:
        """Connect integration with external provider."""
        with RequestTracker(user_id=user_id, operation="connect_integration") as tracker:
            try:
                tracking_context = domain_logger.operation_start("connect_integration", user_id=str(user_id), provider=provider, external_user_id=external_user_id, has_meta=meta is not None)

                update_data = IntegrationAccountUpdate(
                    external_user_id=external_user_id,
                    status="connected",
                    meta=meta or {},
                    connected_at=utcnow()
                )

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = IntegrationRepository(uow.session)

                    result: IntegrationAccountOut | None = await repository.update(user_id, provider, update_data)
                    if not result:
                        raise NotFound(f"Integration {provider} not found")

                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "provider": provider,
                        "external_user_id": external_user_id,
                        "integration_id": str(result.id)
                    })
                    domain_logger.business_event("integration_connected", {
                        "user_id": str(user_id),
                        "provider": provider,
                        "external_user_id": external_user_id,
                        "integration_id": str(result.id)
                    })
                    tracker.log_success(
                        provider=provider,
                        external_user_id=external_user_id,
                        integration_id=str(result.id)
                    )
                    
                    return result
            except NotFound:
                error_id = tracker.log_error(NotFound(f"Integration {provider} not found"), context={
                    "user_id": str(user_id),
                    "provider": provider
                })
                domain_logger.operation_error(tracking_context, f"Integration {provider} not found", {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "provider": provider
                })
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "provider": provider,
                    "external_user_id": external_user_id
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "provider": provider
                })
                raise BadRequest(f"Failed to connect integration (Error ID: {error_id})")

    @trace_async
    async def disconnect_integration(
        self, user_id: UUID, provider: IntegrationType, reason: str | None = None, locale: str = "en-US"
    ) -> IntegrationAccountOut | None:
        """Disconnect integration."""
        with RequestTracker(user_id=user_id, operation="disconnect_integration") as tracker:
            try:
                tracking_context = domain_logger.operation_start("disconnect_integration", user_id=str(user_id), provider=provider, reason=reason)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = IntegrationRepository(uow.session)

                    existing = await repository.get_by_user_provider(user_id, provider)
                    if not existing:
                        raise NotFound(f"Integration {provider} not found")

                    if existing.status == "disconnected":
                        domain_logger.operation_success(tracking_context, {
                            "user_id": str(user_id),
                            "provider": provider,
                            "already_disconnected": True
                        })
                        tracker.log_success(provider=provider, already_disconnected=True)
                        existing_result: IntegrationAccountOut = existing
                        return existing_result

                    # Clear auth data for security and update status
                    cleared_meta = {
                        "disconnected_at": utcnow().isoformat(),
                        "reason": reason or "user_requested"
                    }

                    update_data = IntegrationAccountUpdate(
                        status="disconnected",
                        meta=cleared_meta,
                        external_user_id=""
                    )

                    result: IntegrationAccountOut | None = await repository.update(user_id, provider, update_data)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "provider": provider,
                        "reason": reason,
                        "integration_id": str(result.id) if result else None
                    })
                    domain_logger.business_event("integration_disconnected", {
                        "user_id": str(user_id),
                        "provider": provider,
                        "reason": reason or "user_requested",
                        "integration_id": str(result.id) if result else None
                    })
                    tracker.log_success(
                        provider=provider,
                        reason=reason,
                        integration_id=str(result.id) if result else None
                    )
                    
                    return result
            except NotFound:
                error_id = tracker.log_error(NotFound(f"Integration {provider} not found"), context={
                    "user_id": str(user_id),
                    "provider": provider
                })
                domain_logger.operation_error(tracking_context, f"Integration {provider} not found", {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "provider": provider
                })
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "provider": provider,
                    "reason": reason
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "provider": provider
                })
                raise BadRequest(f"Failed to disconnect integration (Error ID: {error_id})")

    @trace_async
    async def delete_integration(self, user_id: UUID, provider: IntegrationType) -> None:
        """Delete integration."""
        with RequestTracker(user_id=user_id, operation="delete_integration") as tracker:
            try:
                tracking_context = domain_logger.operation_start("delete_integration", user_id=str(user_id), 
                                            context={"provider": provider})
                
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = IntegrationRepository(uow.session)
                    await repository.delete(user_id, provider)
                
                domain_logger.operation_success(tracking_context, user_id=str(user_id))
                domain_logger.business_event("integration_deleted", user_id=str(user_id), 
                                           context={"provider": provider})
                
                tracker.log_success()
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id), "provider": provider})
                domain_logger.operation_error(tracking_context, error_id=error_id, user_id=str(user_id))
                logger.error("Failed to delete integration", extra={
                    "user_id": str(user_id), "provider": provider, "error": str(e)
                })
                raise BadRequest("Failed to delete integration")

    @trace_async
    async def integration_exists(self, user_id: UUID, provider: IntegrationType) -> bool:
        """Check if integration exists."""
        with RequestTracker(user_id=user_id, operation="integration_exists") as tracker:
            try:
                tracking_context = domain_logger.operation_start("integration_exists", user_id=str(user_id), 
                                            context={"provider": provider})
                
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = IntegrationRepository(uow.session)
                    result: bool = await repository.exists(user_id, provider)
                
                domain_logger.operation_success(tracking_context, user_id=str(user_id), 
                                              context={"exists": result})
                
                tracker.log_success(result_id=str(result))
                return result
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id), "provider": provider})
                domain_logger.operation_error(tracking_context, error_id=error_id, user_id=str(user_id))
                raise BadRequest("Failed to check integration existence")

    @trace_async
    async def generate_instagram_auth_url(self, user_id: UUID) -> dict[str, str]:
        """Generate Instagram OAuth authorization URL."""
        with RequestTracker(user_id=user_id, operation="generate_instagram_auth_url") as tracker:
            try:
                tracking_context = domain_logger.operation_start("generate_instagram_auth_url", user_id=str(user_id))
                
                if not config.META_APP_ID or not config.META_APP_SECRET:
                    error_id = tracker.log_error(BadRequest("Instagram integration not configured"), context={
                        "user_id": str(user_id)
                    })
                    domain_logger.operation_error(tracking_context, error_id=error_id, 
                                                user_id=str(user_id))
                    raise BadRequest("Instagram integration not configured")

                # Generate state for CSRF protection
                state = str(uuid.uuid4())

                # Store state data in Redis
                state_data = {
                    "user_id": str(user_id),
                    "timestamp": utcnow().isoformat()
                }

                redis_client = get_redis_client()
                key = f"instagram_oauth_state:{state}"

                try:
                    await redis_client.set(key, state_data, ex=3600)  # 1 hour expiration
                    logger.info("Instagram OAuth state stored", extra={
                        "user_id": str(user_id), "state": state
                    })
                except Exception as e:
                    error_id = tracker.log_error(e, context={
                        "user_id": str(user_id), "state": state
                    })
                    domain_logger.operation_error(tracking_context, error_id=error_id,
                                                user_id=str(user_id))
                    logger.error("Failed to store Instagram OAuth state", extra={
                        "user_id": str(user_id), "error": str(e)
                    })
                    raise BadRequest("Failed to initialize OAuth flow")

                # Use webhook.flerity.com for all environments
                redirect_uri = "https://webhook.flerity.com/integrations/instagram/callback"

                # Instagram OAuth scopes
                scopes = ["instagram_business_basic", "instagram_business_manage_messages"]

                # Build authorization URL
                auth_url = (
                    f"https://www.instagram.com/oauth/authorize"
                    f"?client_id={config.META_APP_ID}"
                    f"&redirect_uri={redirect_uri}"
                    f"&scope={','.join(scopes)}"
                    f"&response_type=code"
                    f"&state={state}"
                )

                result = {"authorization_url": auth_url, "state": state}
                
                domain_logger.operation_success(tracking_context, user_id=str(user_id))
                domain_logger.business_event("instagram_auth_url_generated", user_id=str(user_id), 
                                           context={"state": state})
                
                tracker.log_success(result_id=state)
                return result
                
            except BadRequest:
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={"user_id": str(user_id)})
                domain_logger.operation_error(tracking_context, error_id=error_id,
                                            user_id=str(user_id))
                raise BadRequest("Failed to generate Instagram auth URL")

    @trace_async
    async def process_instagram_webhook(self, payload: dict[str, Any]) -> None:
        """Process Instagram webhook messages, edits, reactions."""
        with RequestTracker(operation="process_instagram_webhook") as tracker:
            try:
                # Validate payload is a dictionary
                if not isinstance(payload, dict):
                    logger.error("Instagram webhook payload is not a dictionary", extra={
                        "payload_type": type(payload).__name__,
                        "payload": str(payload)[:200]  # Log first 200 chars
                    })
                    raise ValueError(f"Expected dict payload, got {type(payload).__name__}")
                
                tracking_context = domain_logger.operation_start("process_instagram_webhook", 
                                            context={"entry_count": len(payload.get("entry", []))})
                
                logger.debug("Processing Instagram webhook", extra={
                    "has_payload": bool(payload),
                    "entry_count": len(payload.get("entry", []))
                })

                for entry in payload.get("entry", []):
                    # Handle both 'changes' (old format) and 'messaging' (new format)
                    changes = entry.get("changes", [])
                    messaging = entry.get("messaging", [])

                    # Process changes format
                    for change in changes:
                        field = change.get("field")

                        # Só processa mensagens, edições, reações e visualizações
                        if field not in ["messages", "message_edit", "message_reactions", "messaging_seen"]:
                            logger.debug("Skipping non-message field", extra={"field": field})
                            continue

                        value = change.get("value", {})
                        await self._process_instagram_event(value, field)

                    # Process messaging format
                    for message_event in messaging:
                        # Determinar o tipo de evento baseado nos campos presentes
                        if "message" in message_event:
                            await self._process_instagram_event(message_event, "messages")
                        elif "read" in message_event:
                            await self._process_instagram_event(message_event, "messaging_seen")
                        elif "reaction" in message_event:
                            await self._process_instagram_event(message_event, "message_reactions")
                        elif "message_edit" in message_event:
                            await self._process_instagram_event(message_event, "message_edit")
                        else:
                            logger.warning("Unknown Instagram event type", extra={
                                "event": message_event
                            })

                domain_logger.operation_success(tracking_context, 
                                              context={"entries_processed": len(payload.get("entry", []))})
                domain_logger.business_event("instagram_webhook_processed", 
                                           context={"entries_count": len(payload.get("entry", []))})
                
                tracker.log_success()
                
            except Exception as e:
                error_id = tracker.log_error(e, context={"payload_keys": list(payload.keys()) if payload else []})
                domain_logger.operation_error(tracking_context, error_id=error_id)
                raise

    async def _process_instagram_event(self, value: dict[str, Any], field: str) -> None:
        """Process individual Instagram event."""
        # Validate that value is a dictionary
        if not isinstance(value, dict):
            logger.warning("Instagram event value is not a dictionary", extra={
                "value_type": type(value).__name__,
                "field": field,
                "value": str(value)[:100]  # Log first 100 chars for debugging
            })
            return
            
        sender_id = value.get("sender", {}).get("id")
        recipient_id = value.get("recipient", {}).get("id")
        message = value.get("message", {})
        is_echo = message.get("is_echo", False)

        logger.debug("Instagram event received", extra={
            "field": field,
            "has_sender": bool(sender_id),
            "has_recipient": bool(recipient_id),
            "is_echo": is_echo
        })

        if not sender_id or not recipient_id:
            logger.warning("Missing sender or recipient", extra={
                "has_sender": bool(sender_id),
                "has_recipient": bool(recipient_id)
            })
            return

        # Determine our user ID based on echo status
        if is_echo:
            # Echo message: sender is our user, recipient is external contact
            our_instagram_id = sender_id
            contact_instagram_id = recipient_id
            logger.debug("Echo message detected", extra={
                "has_our_user": bool(our_instagram_id),
                "has_contact": bool(contact_instagram_id)
            })
        else:
            # Regular message: recipient is our user, sender is external contact
            our_instagram_id = recipient_id
            contact_instagram_id = sender_id

        try:
            logger.info("TRACE: Starting user lookup by Instagram ID", extra={
                "our_instagram_id": our_instagram_id,
                "contact_instagram_id": contact_instagram_id
            })
            
            # 1. Encontrar nosso usuário pela integração Instagram
            our_user_id = await self._find_user_by_instagram_id(our_instagram_id)

            logger.info("TRACE: User lookup completed", extra={
                "our_instagram_id": our_instagram_id,
                "found_user": bool(our_user_id),
                "user_id": str(our_user_id) if our_user_id else None
            })

            if not our_user_id:
                logger.warning("No user found for Instagram ID")
                return

            logger.info("TRACE: Starting thread creation/lookup", extra={
                "user_id": str(our_user_id),
                "contact_instagram_id": contact_instagram_id
            })

            # 2. Buscar ou criar thread (com retry para cache invalidation)
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    logger.info("TRACE: Creating UoW for thread operations", extra={
                        "attempt": attempt + 1,
                        "user_id": str(our_user_id)
                    })
                    
                    async with async_uow_factory(self.session_factory, user_id=str(our_user_id))() as uow:
                        logger.info("TRACE: UoW created, calling _get_or_create_instagram_thread", extra={
                            "user_id": str(our_user_id),
                            "contact_instagram_id": contact_instagram_id
                        })
                        
                        thread = await self._get_or_create_instagram_thread(
                            uow.session, our_user_id, contact_instagram_id
                        )

                        logger.info("TRACE: Thread operation completed successfully", extra={
                            "thread_id": str(thread["id"]),
                            "thread_name": thread.get("contact_name"),
                            "user_id": str(our_user_id)
                        })

                        logger.info("TRACE: Starting message save operation", extra={
                            "thread_id": str(thread["id"]),
                            "field": field,
                            "message_type": "echo" if value.get("message", {}).get("is_echo", False) else "received"
                        })

                        # 3. Processar mensagem baseada no tipo
                        await self._save_instagram_message(
                            uow.session, thread["id"], field, value
                        )

                        logger.info("TRACE: Message saved successfully, updating thread activity", extra={
                            "thread_id": str(thread["id"])
                        })

                        # 4. Sempre atualizar last_activity da thread (mesmo para eventos não salvos)
                        from flerity_core.domain.threads.schemas import threads_table
                        
                        logger.info("TRACE: Preparing thread activity update", extra={
                            "thread_id": str(thread["id"])
                        })
                        
                        update_stmt = sa.update(threads_table).where(
                            threads_table.c.id == thread["id"]
                        ).values(last_activity=utcnow())
                        
                        logger.info("TRACE: Executing thread activity update", extra={
                            "thread_id": str(thread["id"])
                        })
                        
                        await uow.session.execute(update_stmt)

                        logger.info("TRACE: Thread activity updated, preparing to commit transaction", extra={
                            "thread_id": str(thread["id"])
                        })

                        await uow.commit()
                        
                        logger.info("TRACE: Transaction committed successfully - webhook processing complete", extra={
                            "thread_id": str(thread["id"]),
                            "user_id": str(our_user_id),
                            "field": field
                        })
                        
                        break  # Success, exit retry loop

                except sa.exc.NotSupportedError as e:
                    if "InvalidCachedStatementError" in str(e) and attempt < max_retries - 1:
                        logger.warning("Database cache invalidated, retrying", extra={
                            "attempt": attempt + 1,
                            "error": str(e)
                        })
                        continue
                    else:
                        raise
                except Exception:
                    raise

            logger.info("TRACE: Instagram message processing completed successfully", extra={
                "user_id": str(our_user_id),
                "thread_id": str(thread["id"]),
                "field": field,
                "sender_id": sender_id,
                "is_echo": is_echo,
                "processing_status": "complete"
            })

        except Exception as e:
            logger.error("Failed to process Instagram message", extra={
                "error": str(e),
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "field": field
            })
            raise

    async def _find_user_by_instagram_id(self, instagram_id: str) -> UUID | None:
        """Find our user by their Instagram external_user_id."""

        async with async_uow_factory(self.session_factory)() as uow:
            # First, let's see all Instagram integrations
            debug_stmt = sa.select(
                integrations_accounts_table.c.user_id,
                integrations_accounts_table.c.external_user_id,
                integrations_accounts_table.c.status,
                integrations_accounts_table.c.provider
            ).where(integrations_accounts_table.c.provider == "instagram")

            debug_result = await uow.session.execute(debug_stmt)
            debug_rows = debug_result.fetchall()
            for row in debug_rows:
                pass  # Debug loop

            # Now the actual lookup
            stmt = sa.select(integrations_accounts_table.c.user_id).where(
                integrations_accounts_table.c.provider == "instagram",
                integrations_accounts_table.c.external_user_id == instagram_id,
                integrations_accounts_table.c.status == "connected"
            )
            result = await uow.session.execute(stmt)
            row = result.fetchone()
            found_user = row[0] if row else None  # Already a UUID object, no conversion needed
            return found_user

    @trace_async
    async def _get_instagram_access_token(self, user_id: UUID) -> dict[str, Any] | None:
        """Get Instagram access token for user."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            stmt = sa.select(
                integrations_accounts_table.c.meta,
                integrations_accounts_table.c.connected_at
            ).where(
                integrations_accounts_table.c.user_id == user_id,
                integrations_accounts_table.c.provider == "instagram",
                integrations_accounts_table.c.status == "connected"
            )
            result = await uow.session.execute(stmt)
            row = result.fetchone()

            if not row:
                return None

            meta = row[0] or {}
            access_token = meta.get("access_token")

            if not access_token:
                return None

            return {
                "access_token": access_token,
                "connected_at": row[1],
                "meta": meta
            }

    @trace_async
    async def _refresh_instagram_token(self, current_token: str) -> str | None:
        """Refresh Instagram access token."""
        if not HTTPX_ASYNC_AVAILABLE:
            logger.error("httpx.AsyncClient not available - cannot refresh Instagram token", extra={
                "httpx_version": getattr(httpx, '__version__', 'unknown')
            })
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.instagram.com/refresh_access_token",
                    params={
                        "grant_type": "ig_refresh_token",
                        "access_token": current_token
                    },
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                else:
                    logger.warning("Failed to refresh Instagram token", extra={
                        "status_code": response.status_code
                    })
                    return None

        except Exception as e:
            logger.warning("Error refreshing Instagram token, using existing token", extra={
                "error": str(e)
            })
            return None

    @trace_async
    async def _get_instagram_user_info(self, user_instagram_id: str, access_token: str) -> dict[str, Any] | None:
        """Get Instagram user information via Graph API."""
        logger.info("TRACE: Starting Instagram user info fetch", extra={
            "user_instagram_id": user_instagram_id,
            "has_access_token": bool(access_token)
        })
        
        if not HTTPX_ASYNC_AVAILABLE:
            logger.error("httpx.AsyncClient not available - cannot fetch Instagram user info", extra={
                "user_instagram_id": user_instagram_id,
                "httpx_version": getattr(httpx, '__version__', 'unknown')
            })
            return None
            
        try:
            url = f"https://graph.instagram.com/v24.0/{user_instagram_id}?access_token={access_token}"
            
            logger.info("TRACE: Making HTTP request to Instagram API", extra={
                "user_instagram_id": user_instagram_id,
                "url_base": "https://graph.instagram.com/v24.0/"
            })

            async with httpx.AsyncClient() as client:
                logger.info("TRACE: HTTP client created, sending request", extra={
                    "user_instagram_id": user_instagram_id
                })
                
                response = await client.get(url, timeout=5.0)
                
                logger.info("TRACE: HTTP response received", extra={
                    "user_instagram_id": user_instagram_id,
                    "status_code": response.status_code,
                    "response_size": len(response.content) if response.content else 0
                })
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("TRACE: Instagram API response parsed successfully", extra={
                        "user_instagram_id": user_instagram_id,
                        "has_username": "username" in result,
                        "has_name": "name" in result
                    })
                    
                    logger.info("TRACE: Returning Instagram user info - method completing", extra={
                        "user_instagram_id": user_instagram_id,
                        "result_keys": list(result.keys()) if result else []
                    })
                    
                    return result
                else:
                    logger.warning("Failed to get Instagram user info", extra={
                        "status_code": response.status_code,
                        "user_instagram_id": user_instagram_id,
                        "response_text": response.text[:200] if response.text else ""
                    })
                    return None

        except Exception as e:
            logger.warning("Error getting Instagram user info, using fallback", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "user_instagram_id": user_instagram_id
            })
            return None
            return None

    @trace_async
    async def get_instagram_username(self, user_id: UUID, contact_instagram_id: str) -> dict[str, str]:
        """Get real Instagram username and profile pic for contact."""
        try:
            # 1. Get access token
            token_info = await self._get_instagram_access_token(user_id)
            if not token_info:
                logger.info("No Instagram access token found, using fallback name", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id
                })
                return {
                    "name": f"Instagram User {contact_instagram_id}",
                    "username": f"user_{contact_instagram_id}",
                    "profile_pic": None
                }

            access_token = token_info["access_token"]
            connected_at = token_info["connected_at"]

            # 2. Check if token needs refresh (> 50 days)
            if connected_at and connected_at < utcnow() - timedelta(days=50):
                logger.info("Refreshing Instagram token", extra={"user_id": str(user_id)})
                new_token = await self._refresh_instagram_token(access_token)

                if new_token:
                    # Update token in database
                    try:
                        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                            new_meta = token_info["meta"].copy()
                            new_meta["access_token"] = new_token

                            stmt = sa.update(integrations_accounts_table).where(
                                integrations_accounts_table.c.user_id == user_id,
                                integrations_accounts_table.c.provider == "instagram"
                            ).values(
                                meta=new_meta,
                                connected_at=utcnow()
                            )
                            await uow.session.execute(stmt)
                            await uow.commit()

                        access_token = new_token
                    except Exception as e:
                        logger.warning("Failed to update refreshed token, using old one", extra={
                            "user_id": str(user_id),
                            "error": str(e)
                        })
                else:
                    logger.warning("Failed to refresh token, using old one", extra={"user_id": str(user_id)})

            # 3. Get user info from Graph API (with timeout protection)
            user_info = await self._get_instagram_user_info(contact_instagram_id, access_token)

            logger.info("TRACE: _get_instagram_user_info call completed", extra={
                "user_id": str(user_id),
                "contact_instagram_id": contact_instagram_id,
                "user_info_received": bool(user_info),
                "user_info_keys": list(user_info.keys()) if user_info else []
            })

            logger.info("TRACE: Processing user_info data", extra={
                "user_id": str(user_id),
                "contact_instagram_id": contact_instagram_id,
                "processing_step": "start"
            })

            if user_info:
                logger.info("TRACE: Extracting name and username from user_info", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id
                })
                
                logger.info("TRACE: Getting name from user_info", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "has_name_key": "name" in user_info,
                    "name_value_type": type(user_info.get("name")).__name__ if "name" in user_info else "missing"
                })
                
                # Prefer name over username, fallback to generic
                name_from_api = user_info.get("name")
                
                logger.info("TRACE: Name extracted, getting username", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "name_from_api": str(name_from_api)[:50] if name_from_api else None
                })
                
                username_from_api = user_info.get("username")
                
                logger.info("TRACE: Username extracted, building final values", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "username_from_api": str(username_from_api)[:50] if username_from_api else None
                })
                
                name = name_from_api or username_from_api or f"Instagram User {contact_instagram_id}"
                username = username_from_api or f"user_{contact_instagram_id}"
                profile_pic = user_info.get("profile_pic")
                
                logger.info("TRACE: Data extracted, preparing return object", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "contact_name": name,
                    "contact_username": username
                })
                
                logger.info("TRACE: get_instagram_username returning with real data", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "contact_name": name,
                    "contact_username": username
                })
                
                return {
                    "name": name,
                    "username": username,
                    "profile_pic": profile_pic
                }
            else:
                logger.info("TRACE: get_instagram_username returning with fallback data", extra={
                    "user_id": str(user_id),
                    "contact_instagram_id": contact_instagram_id,
                    "reason": "no_user_info"
                })
                return {
                    "name": f"Instagram User {contact_instagram_id}",
                    "username": f"user_{contact_instagram_id}",
                    "profile_pic": None
                }

        except Exception as e:
            logger.warning("Error in get_instagram_username, using fallback", extra={
                "error": str(e),
                "user_id": str(user_id),
                "contact_instagram_id": contact_instagram_id
            })
            return {
                "name": f"Instagram User {contact_instagram_id}",
                "username": f"user_{contact_instagram_id}",
                "profile_pic": None
            }

        except Exception as e:
            logger.error("Error getting Instagram username", extra={
                "user_id": str(user_id),
                "contact_id": contact_instagram_id,
                "error": str(e)
            })
            return {
                "name": f"Instagram User {contact_instagram_id}",
                "username": f"user_{contact_instagram_id}",
                "profile_pic": None
            }

    async def _get_or_create_instagram_thread(self, session, user_id: UUID, contact_instagram_id: str) -> dict:
        """Get existing thread or create new one for Instagram contact."""
        from flerity_core.domain.threads.schemas import threads_table

        logger.info("TRACE: Starting thread lookup in database", extra={
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id
        })

        # Buscar thread existente usando contact_id (Instagram ID é imutável)
        stmt = sa.select(threads_table).where(
            threads_table.c.user_id == user_id,
            threads_table.c.channel == "instagram",
            threads_table.c.contact_id == contact_instagram_id
        )
        result = await session.execute(stmt)
        row = result.fetchone()

        logger.info("TRACE: Database thread lookup completed", extra={
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id,
            "thread_found": bool(row)
        })

        if row:
            existing_thread = dict(row._mapping)

            logger.info("TRACE: Found existing thread", extra={
                "thread_id": str(existing_thread['id']),
                "contact_name": existing_thread['contact_name'],
                "needs_username_update": existing_thread['contact_name'].startswith('Instagram User')
            })

            # Se thread existe mas tem nome genérico, tentar buscar nome real (async, não bloquear)
            if existing_thread['contact_name'].startswith('Instagram User'):
                logger.info("TRACE: Scheduling background username update for existing thread", extra={
                    "thread_id": str(existing_thread['id'])
                })
                # Schedule username fetch in background, don't wait for it
                asyncio.create_task(self._update_thread_username_async(user_id, existing_thread['id'], contact_instagram_id))

            logger.info("TRACE: Returning existing thread", extra={
                "thread_id": str(existing_thread['id'])
            })
            return existing_thread

        logger.info("TRACE: No existing thread found, creating new thread", extra={
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id
        })

        # Para nova thread, usar nome genérico inicialmente para não bloquear
        # O nome real será atualizado em background
        thread_data = {
            "user_id": user_id,
            "channel": "instagram",
            "contact_id": contact_instagram_id,
            "contact_handle": f"user_{contact_instagram_id}",
            "contact_name": f"Instagram User {contact_instagram_id}",
            "contact_profile_pic": None,
            "last_activity": utcnow()
        }

        logger.info("TRACE: Inserting new thread into database", extra={
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id,
            "thread_name": thread_data["contact_name"]
        })

        # Use INSERT ON CONFLICT to handle race condition when multiple webhooks arrive simultaneously
        stmt = sa.insert(threads_table).values(**thread_data).on_conflict_do_update(
            index_elements=["user_id", "channel", "contact_id"],
            set_={"last_activity": thread_data["last_activity"]}
        ).returning(threads_table)
        result = await session.execute(stmt)
        row = result.fetchone()
        new_thread = dict(row._mapping)

        logger.info("TRACE: New thread created successfully", extra={
            "thread_id": str(new_thread['id']),
            "user_id": str(user_id)
        })

        logger.info("TRACE: Scheduling background username update for new thread", extra={
            "thread_id": str(new_thread['id'])
        })
        # Schedule username fetch in background
        asyncio.create_task(self._update_thread_username_async(user_id, new_thread['id'], contact_instagram_id))

        logger.info("TRACE: Starting thread tracking setup", extra={
            "thread_id": str(new_thread['id'])
        })

        # Ativar assistência por padrão para novas threads
        try:
            from flerity_core.domain.threads.tracking.repository import ThreadTrackingRepository
            from flerity_core.domain.threads.tracking.schemas import (
                ThreadTrackingConfigurationCreate,
            )

            logger.info("TRACE: Creating tracking repository", extra={
                "thread_id": str(new_thread['id'])
            })

            tracking_repo = ThreadTrackingRepository(session)
            tracking_config = ThreadTrackingConfigurationCreate(
                thread_id=new_thread['id'],
                is_active=True
            )

            logger.info("TRACE: Creating tracking configuration", extra={
                "thread_id": str(new_thread['id'])
            })

            logger.info("TRACE: About to call tracking_repo.create", extra={
                "thread_id": str(new_thread['id'])
            })

            await tracking_repo.create(tracking_config, user_id)

            logger.info("TRACE: tracking_repo.create completed successfully", extra={
                "thread_id": str(new_thread['id'])
            })

            logger.info("TRACE: Thread tracking auto-enabled for new thread", extra={
                "thread_id": str(new_thread['id']),
                "user_id": str(user_id),
                "channel": "instagram",
                "contact_id": contact_instagram_id
            })
        except Exception as e:
            # Não falhar a criação da thread se o tracking falhar
            logger.warning("TRACE: Failed to auto-enable tracking for new thread", extra={
                "thread_id": str(new_thread['id']),
                "user_id": str(user_id),
                "error": str(e)
            })

        logger.info("TRACE: Returning new thread", extra={
            "thread_id": str(new_thread['id'])
        })

        return new_thread

    async def _update_thread_username_async(self, user_id: UUID, thread_id: UUID, contact_instagram_id: str) -> None:
        """Update thread username in background without blocking webhook processing."""
        logger.info("TRACE: Background username update task started", extra={
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id
        })
        
        logger.debug("DEBUG: Starting background username update", extra={
            "thread_id": str(thread_id),
            "user_id": str(user_id),
            "contact_instagram_id": contact_instagram_id
        })
        
        try:
            logger.debug("DEBUG: Calling get_instagram_username with timeout", extra={
                "thread_id": str(thread_id),
                "timeout_seconds": 10
            })
            
            # Get real username with timeout protection
            user_data = await asyncio.wait_for(
                self.get_instagram_username(user_id, contact_instagram_id),
                timeout=10.0  # 10 second timeout
            )

            logger.info("TRACE: Background task - get_instagram_username completed", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "user_name": user_data.get("name", ""),
                "is_fallback": user_data["name"].startswith('Instagram User')
            })

            logger.debug("DEBUG: Username fetch completed", extra={
                "thread_id": str(thread_id),
                "user_name": user_data.get("name", ""),
                "is_fallback": user_data["name"].startswith('Instagram User')
            })

            # Only update if we got a real name (not fallback)
            if not user_data["name"].startswith('Instagram User'):
                logger.debug("DEBUG: Updating thread with real username", extra={
                    "thread_id": str(thread_id),
                    "new_name": user_data["name"]
                })
                
                from flerity_core.domain.threads.schemas import threads_table
                
                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    update_stmt = sa.update(threads_table).where(
                        threads_table.c.id == thread_id
                    ).values(
                        contact_name=user_data["name"],
                        contact_handle=user_data["username"],
                        contact_profile_pic=user_data["profile_pic"]
                    )
                    await uow.session.execute(update_stmt)
                    await uow.commit()

                logger.info("Thread username updated in background", extra={
                    "thread_id": str(thread_id),
                    "user_id": str(user_id),
                    "contact_name": user_data["name"]
                })
            else:
                logger.debug("DEBUG: Keeping fallback name (no real name available)", extra={
                    "thread_id": str(thread_id),
                    "fallback_name": user_data["name"]
                })

        except asyncio.TimeoutError:
            logger.warning("Username fetch timed out, keeping fallback name", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "contact_instagram_id": contact_instagram_id,
                "timeout_seconds": 10
            })
        except Exception as e:
            logger.warning("Failed to update thread username in background", extra={
                "thread_id": str(thread_id),
                "user_id": str(user_id),
                "error": str(e),
                "error_type": type(e).__name__
            })

    async def _save_instagram_message(self, session, thread_id: UUID, field: str, value: dict[str, Any]) -> None:
        """Save Instagram message/edit/reaction to messages table."""

        from flerity_core.domain.threads.schemas import messages_table

        logger.info("TRACE: Starting message save operation", extra={
            "thread_id": str(thread_id),
            "field": field,
            "has_value": bool(value)
        })

        # Determinar se é mensagem enviada ou recebida
        is_echo = value.get("message", {}).get("is_echo", False)
        sender_type = "user" if is_echo else "contact"

        logger.info("TRACE: Message type determined", extra={
            "thread_id": str(thread_id),
            "field": field,
            "is_echo": is_echo,
            "sender_type": sender_type
        })

        # Extrair dados baseado no tipo
        message_data = {
            "thread_id": thread_id,
            "sender": sender_type,  # "user" para enviadas, "contact" para recebidas
            "timestamp": utcnow(),
            "metadata": {
                "instagram_user_id": value.get("sender", {}).get("id"),
                "field_type": field,
                "is_echo": is_echo,
                "raw_payload": value
            }
        }

        logger.info("TRACE: Processing field-specific data", extra={
            "thread_id": str(thread_id),
            "field": field
        })

        if field == "messages":
            message = value.get("message", {})
            message_data["text"] = message.get("text")
            message_data["metadata"]["instagram_message_id"] = message.get("mid")

        elif field == "message_edit":
            edit = value.get("message_edit", {})
            message_data["text"] = f"[EDITADO] {edit.get('text', '')}"
            message_data["metadata"]["instagram_message_id"] = edit.get("mid")
            message_data["metadata"]["edit_number"] = edit.get("num_edit")

        elif field == "message_reactions":
            reaction = value.get("reaction", {})
            emoji = reaction.get("emoji", "")
            message_data["text"] = emoji
            message_data["metadata"]["instagram_message_id"] = reaction.get("mid")
            message_data["metadata"]["reaction_type"] = reaction.get("reaction")

        elif field == "messaging_seen":
            read = value.get("read", {})
            message_data["text"] = "seen"
            message_data["metadata"]["last_read_message_id"] = read.get("mid")
            message_data["metadata"]["read_timestamp"] = value.get("timestamp")

        logger.info("TRACE: Message data prepared, inserting into database", extra={
            "thread_id": str(thread_id),
            "field": field,
            "has_text": bool(message_data.get("text")),
            "sender": sender_type
        })

        # Inserir mensagem (sempre, mesmo se null - filtraremos na API)
        stmt = sa.insert(messages_table).values(**message_data)
        await session.execute(stmt)

        logger.info("TRACE: Message inserted, verifying count", extra={
            "thread_id": str(thread_id)
        })

        # Verificar se a mensagem foi inserida
        verify_stmt = sa.select(sa.func.count()).select_from(messages_table).where(
            messages_table.c.thread_id == thread_id
        )
        count_result = await session.execute(verify_stmt)
        message_count = count_result.scalar()

        logger.info("TRACE: Message save operation completed", extra={
            "thread_id": str(thread_id),
            "field": field,
            "total_messages": message_count
        })



class WhatsAppPairingService:
    """Service for WhatsApp pairing sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def create_pairing_session(
        self, user_id: UUID, session_code: str, expires_at: datetime
    ) -> WhatsAppPairingSessionOut:
        """Create new pairing session."""
        try:
            async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                repository = WhatsAppPairingRepository(uow.session)

                session_data = WhatsAppPairingSessionCreate(
                    user_id=user_id,
                    session_code=session_code,
                    expires_at=expires_at,
                    status="issued"
                )

                result: WhatsAppPairingSessionOut = await repository.create_session(session_data)
                return result
        except Exception as e:
            logger.error("Failed to create pairing session", extra={
                "user_id": str(user_id), "session_code": session_code, "error": str(e)
            })
            raise BadRequest("Failed to create pairing session")

    @trace_async
    async def get_session_by_code(self, session_code: str, user_id: UUID | None = None) -> WhatsAppPairingSessionOut | None:
        """Get pairing session by code."""
        # Use system context for session lookup by code
        async with async_uow_factory(self.session_factory, user_id=str(user_id) if user_id else None)() as uow:
            repository = WhatsAppPairingRepository(uow.session)
            result: WhatsAppPairingSessionOut | None = await repository.get_by_code(session_code)
            return result

    @trace_async
    async def get_user_sessions(self, user_id: UUID) -> list[WhatsAppPairingSessionOut]:
        """Get WhatsApp pairing sessions for user."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = WhatsAppPairingRepository(uow.session)
            result: list[WhatsAppPairingSessionOut] = await repository.get_by_user(user_id)
            return result

    @trace_async
    async def consume_pairing_code(self, session_code: str) -> WhatsAppPairingSessionOut:
        """Consume WhatsApp pairing code."""
        try:
            # Use system context for consuming pairing codes
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repository = WhatsAppPairingRepository(uow.session)

                session = await repository.get_by_code(session_code)
                if not session:
                    raise NotFound("Pairing session not found")

                if session.status != "issued":
                    raise BadRequest(f"Pairing session is {session.status}")

                # Update session status
                result: WhatsAppPairingSessionOut = await repository.update_status(session.id, "consumed")
                return result
        except (NotFound, BadRequest):
            raise
        except Exception as e:
            logger.error("Failed to consume pairing code", extra={
                "session_code": session_code, "error": str(e)
            })
            raise BadRequest("Failed to consume pairing code")

    @trace_async
    async def expire_old_sessions(self) -> int:
        """Expire old pairing sessions."""
        try:
            # Use system context for cleanup operations
            async with async_uow_factory(self.session_factory, user_id=None)() as uow:
                repository = WhatsAppPairingRepository(uow.session)
                result: int = await repository.expire_old_sessions()
                return result
        except Exception as e:
            logger.error("Failed to expire old sessions", extra={"error": str(e)})
            raise BadRequest("Failed to expire sessions")


def create_integration_service(session_factory: async_sessionmaker[AsyncSession]) -> IntegrationService:
    """Factory function for IntegrationService."""
    return IntegrationService(session_factory)


def create_whatsapp_pairing_service(session_factory: async_sessionmaker[AsyncSession]) -> WhatsAppPairingService:
    """Factory function for WhatsAppPairingService."""
    return WhatsAppPairingService(session_factory)
