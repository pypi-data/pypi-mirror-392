"""Devices service for business logic orchestration and device management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.domain_logger import get_domain_logger
from ...utils.errors import BadRequest, NotFound
from ...utils.logging import get_safe_logger
from ...utils.request_tracking import RequestTracker
from ...utils.tracing import trace_async
from .repository import DevicesRepository
from .schemas import DeviceCreate, DeviceOut, DeviceUpdate, Platform

logger = get_safe_logger(__name__)
domain_logger = get_domain_logger(__name__)


class DevicesService:
    """Service for device registration and management."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @trace_async
    async def register_device(self, user_id: UUID, data: DeviceCreate, locale: str = "en-US") -> DeviceOut:
        """Register or update device (idempotent)."""
        with RequestTracker(user_id=user_id, operation="register_device") as tracker:
            try:
                tracking_context = domain_logger.operation_start("register_device", user_id=str(user_id), device_id=data.device_id, platform=data.platform, is_sandbox=data.is_sandbox)

                from ...utils.i18n import t

                # Validate required fields
                if not data.device_id or not data.device_id.strip():
                    raise BadRequest("Device ID is required")
                if not data.push_token or not data.push_token.strip():
                    raise BadRequest("Push token is required")
                if not data.platform:
                    raise BadRequest("Platform is required")

                # Ensure user_id is properly set and converted to UUID
                data.user_id = user_id

                # Ensure user_id is passed as string to UoW
                user_id_str = str(user_id)
                async with async_uow_factory(self.session_factory, user_id=user_id_str)() as uow:
                    repository = DevicesRepository(uow.session)
                    device: DeviceOut = await repository.upsert_device(data, locale)
                    await uow.commit()
                    
                    domain_logger.operation_success(tracking_context, {
                        "user_id": str(user_id),
                        "device_id": data.device_id,
                        "platform": data.platform,
                        "device_uuid": str(device.id)
                    })
                    domain_logger.business_event("device_registered", {
                        "user_id": str(user_id),
                        "device_id": data.device_id,
                        "platform": data.platform,
                        "device_uuid": str(device.id),
                        "is_sandbox": data.is_sandbox
                    })
                    tracker.log_success(
                        device_id=data.device_id,
                        platform=data.platform,
                        device_uuid=str(device.id)
                    )
                    
                    return device
            except BadRequest:
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                # Check if it's a foreign key violation (user doesn't exist)
                if "foreign key constraint" in str(e).lower() and "user" in str(e).lower():
                    error_id = tracker.log_error(e, context={
                        "user_id": str(user_id),
                        "device_id": data.device_id
                    })
                    domain_logger.operation_error(tracking_context, str(e), {
                        "error_id": error_id,
                        "user_id": str(user_id),
                        "device_id": data.device_id
                    })
                    raise NotFound(f"User {user_id} not found")
                
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": data.device_id,
                    "platform": data.platform
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "user_id": str(user_id),
                    "device_id": data.device_id
                })
                raise BadRequest(f"Failed to register device (Error ID: {error_id})")

        logger.info("Device registered successfully", extra={
            "user_id": str(user_id),
            "device_id": data.device_id,
            "device_uuid": str(device.id)
        })

        # Create SNS endpoint immediately after device registration
        try:
            from ..notifications.push_sender import PushNotificationSender

            logger.info("Creating SNS endpoint for device", extra={
                "device_id": data.device_id,
                "platform": data.platform,
                "is_sandbox": data.is_sandbox
            })

            push_sender = PushNotificationSender()

            # Get platform ARN
            platform_arn = push_sender._get_platform_arn(data.platform, data.is_sandbox)

            if platform_arn:
                # Create endpoint
                endpoint_arn = await push_sender._create_platform_endpoint(
                    platform_arn,
                    data.push_token
                )

                if endpoint_arn:
                    logger.info("SNS endpoint created successfully", extra={
                        "device_id": data.device_id,
                        "endpoint_arn": endpoint_arn
                    })
                else:
                    logger.warning("Failed to create SNS endpoint", extra={
                        "device_id": data.device_id,
                        "platform": data.platform
                    })
            else:
                logger.warning("Platform ARN not configured", extra={
                    "platform": data.platform,
                    "is_sandbox": data.is_sandbox
                })

        except Exception as e:
            # Don't fail device registration if SNS endpoint creation fails
            logger.error("Error creating SNS endpoint (non-fatal)", extra={
                "device_id": data.device_id,
                "error": str(e)
            })

        return device

    @trace_async
    async def get_device(self, device_id: UUID, user_id: UUID) -> DeviceOut | None:
        """Get device by ID."""
        with RequestTracker(user_id=user_id, operation="get_device") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_device", user_id=str(user_id), device_id=str(device_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    result: DeviceOut | None = await repository.get_by_id(device_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "found": result is not None
                })

                tracker.log_success(device_id=str(device_id) if result else None)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to get device (Error ID: {error_id})")

    @trace_async
    async def get_user_device(self, user_id: UUID, device_id: str) -> DeviceOut | None:
        """Get device by user and device ID."""
        with RequestTracker(user_id=user_id, operation="get_user_device") as tracker:
            try:
                if not device_id or not device_id.strip():
                    raise BadRequest("Device ID is required")

                tracking_context = domain_logger.operation_start("get_user_device", user_id=str(user_id), device_id=device_id)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    result: DeviceOut | None = await repository.get_by_device_id(user_id, device_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "found": result is not None
                })

                tracker.log_success(device_id=device_id if result else None)
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": device_id
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to get user device (Error ID: {error_id})")

    @trace_async
    async def list_user_devices(self, user_id: UUID) -> list[DeviceOut]:
        """List all devices for user."""
        with RequestTracker(user_id=user_id, operation="list_user_devices") as tracker:
            try:
                tracking_context = domain_logger.operation_start("list_user_devices", user_id=str(user_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    result: list[DeviceOut] = await repository.list_user_devices(user_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_count": len(result)
                })

                tracker.log_success(device_count=len(result))
                return result

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id)
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to list user devices (Error ID: {error_id})")

    @trace_async
    async def update_device(self, device_id: UUID, data: DeviceUpdate, user_id: UUID) -> DeviceOut:
        """Update device by ID."""
        with RequestTracker(user_id=user_id, operation="update_device") as tracker:
            try:
                # Validate update data has at least one field
                update_fields = data.model_dump(exclude_unset=True)
                if not update_fields:
                    raise BadRequest("At least one field must be provided for update")

                tracking_context = domain_logger.operation_start("update_device", user_id=str(user_id), device_id=str(device_id), update_fields=list(update_fields.keys()))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    device: DeviceOut | None = await repository.update_device(device_id, data)

                if not device:
                    raise NotFound("Device not found or access denied")

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "updated_fields": list(update_fields.keys())
                })

                domain_logger.business_event("device_updated", {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "platform": getattr(device, 'platform', None),
                    "updated_fields": list(update_fields.keys())
                })

                tracker.log_success(device_id=str(device_id))
                return device

            except (NotFound, BadRequest):
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to update device (Error ID: {error_id})")

    @trace_async
    async def update_push_token(self, user_id: UUID, device_id: str, push_token: str) -> DeviceOut:
        """Update push token for specific device."""
        with RequestTracker(user_id=user_id, operation="update_push_token") as tracker:
            try:
                if not device_id or not device_id.strip():
                    raise BadRequest("Device ID is required")
                if not push_token or not push_token.strip():
                    raise BadRequest("Push token is required")

                tracking_context = domain_logger.operation_start("update_push_token", user_id=str(user_id), device_id=device_id)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    device = await repository.get_by_device_id(user_id, device_id)
                    if not device:
                        raise NotFound("Device not found")

                    update_data = DeviceUpdate(
                        push_token=push_token,
                        app_version=None,
                        os_version=None,
                        device_model=None,
                        locale=None,
                        timezone=None
                    )
                    updated_device: DeviceOut | None = await repository.update_device(device.id, update_data)

                    if not updated_device:
                        raise NotFound("Device not found or access denied")

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "device_uuid": str(device.id)
                })

                domain_logger.business_event("push_token_updated", {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "platform": getattr(updated_device, 'platform', None)
                })

                tracker.log_success(device_id=device_id)
                return updated_device

            except (NotFound, BadRequest):
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": device_id
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to update push token (Error ID: {error_id})")

    @trace_async
    async def remove_device(self, device_id: UUID, user_id: UUID) -> None:
        """Remove device by ID."""
        with RequestTracker(user_id=user_id, operation="remove_device") as tracker:
            try:
                tracking_context = domain_logger.operation_start("remove_device", user_id=str(user_id), device_id=str(device_id))

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    await repository.delete_device(device_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                })

                domain_logger.business_event("device_removed", {
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                })

                tracker.log_success(device_id=str(device_id))

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": str(device_id),
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to remove device (Error ID: {error_id})")

    @trace_async
    async def remove_user_device(self, user_id: UUID, device_id: str) -> None:
        """Remove device by user and device ID."""
        with RequestTracker(user_id=user_id, operation="remove_user_device") as tracker:
            try:
                if not device_id or not device_id.strip():
                    raise BadRequest("Device ID is required")

                tracking_context = domain_logger.operation_start("remove_user_device", user_id=str(user_id), device_id=device_id)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    await repository.delete_user_device(user_id, device_id)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "device_id": device_id
                })

                domain_logger.business_event("user_device_removed", {
                    "user_id": str(user_id),
                    "device_id": device_id
                })

                tracker.log_success(device_id=device_id)

            except BadRequest:
                raise
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "device_id": device_id
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "device_id": device_id,
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to remove user device (Error ID: {error_id})")

    @trace_async
    async def get_push_tokens(self, user_id: UUID, platform: Platform | None = None) -> list[str]:
        """Get active push tokens for user, optionally filtered by platform."""
        with RequestTracker(user_id=user_id, operation="get_push_tokens") as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_push_tokens", user_id=str(user_id), platform=str(platform) if platform else None)

                async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
                    repository = DevicesRepository(uow.session)
                    tokens: list[str] = await repository.get_push_tokens(user_id, platform)

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "platform": str(platform) if platform else None,
                    "token_count": len(tokens)
                })

                tracker.log_success(token_count=len(tokens))
                return tokens

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id),
                    "platform": str(platform) if platform else None
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "platform": str(platform) if platform else None,
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to get push tokens (Error ID: {error_id})")

    @trace_async
    async def has_devices(self, user_id: UUID) -> bool:
        """Check if user has any registered devices."""
        with RequestTracker(user_id=user_id, operation="has_devices") as tracker:
            try:
                tracking_context = domain_logger.operation_start("has_devices", user_id=str(user_id))

                # More efficient: get push tokens count instead of full device list
                tokens = await self.get_push_tokens(user_id)
                has_devices = len(tokens) > 0

                domain_logger.operation_success(tracking_context, {
                    "user_id": str(user_id),
                    "has_devices": has_devices,
                    "device_count": len(tokens)
                })

                tracker.log_success(has_devices=has_devices, device_count=len(tokens))
                return has_devices

            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "user_id": str(user_id)
                })

                domain_logger.operation_error(tracking_context, str(e), {
                    "user_id": str(user_id),
                    "error_id": error_id
                })

                raise BadRequest(f"Failed to check device status (Error ID: {error_id})")


def create_devices_service(session_factory: async_sessionmaker[AsyncSession]) -> DevicesService:
    """Factory function for DevicesService."""
    return DevicesService(session_factory)
