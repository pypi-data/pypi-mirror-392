"""Devices repository for managing user devices and push tokens."""

from typing import cast
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.errors import BadRequest, Conflict, NotFound
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from .schemas import DeviceCreate, DeviceOut, DeviceUpdate, Platform, devices_table

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)


class DevicesRepository:
    """Repository for user devices."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_by_id(self, device_id: UUID) -> DeviceOut | None:
        """Get device by ID (RLS enforced)."""
        try:
            tracking_context = domain_logger.operation_start("get_by_id", device_id=str(device_id))

            stmt = sa.select(devices_table).where(devices_table.c.id == device_id)

            result = await self.session.execute(stmt)
            row = result.fetchone()
            device = DeviceOut.model_validate(row._asdict()) if row else None

            domain_logger.operation_success(tracking_context, {
                "device_id": str(device_id),
                "found": device is not None,
                "platform": device.platform if device else None
            })

            return device
        except sa.exc.SQLAlchemyError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "device_id": str(device_id)
            })
            logger.error("Database error getting device by ID", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to retrieve device")
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "device_id": str(device_id)
            })
            logger.error("Unexpected error getting device by ID", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to retrieve device")

    @trace_async
    async def get_by_device_id(self, user_id: UUID, device_id: str) -> DeviceOut | None:
        """Get device by user_id and device_id."""
        if not device_id.strip():
            raise BadRequest("Device ID cannot be empty")

        try:
            stmt = sa.select(devices_table).where(
                sa.and_(
                    devices_table.c.user_id == user_id,
                    devices_table.c.device_id == device_id
                )
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()
            return DeviceOut.model_validate(row._asdict()) if row else None
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error getting device by device_id", extra={
                "user_id": str(user_id), "device_id": device_id, "error": str(e)
            })
            raise BadRequest("Failed to retrieve device")
        except Exception as e:
            logger.error("Unexpected error getting device by device_id", extra={
                "user_id": str(user_id), "device_id": device_id, "error": str(e)
            })
            raise BadRequest("Failed to retrieve device")

    @trace_async
    async def list_user_devices(self, user_id: UUID) -> list[DeviceOut]:
        """List all devices for user."""
        try:
            stmt = (
                sa.select(devices_table)
                .where(devices_table.c.user_id == user_id)
                .order_by(devices_table.c.updated_at.desc())
            )

            result = await self.session.execute(stmt)
            return [DeviceOut.model_validate(row._asdict()) for row in result.fetchall()]
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error listing user devices", extra={"user_id": str(user_id), "error": str(e)})
            raise BadRequest("Failed to retrieve devices")
        except Exception as e:
            logger.error("Unexpected error listing user devices", extra={"user_id": str(user_id), "error": str(e)})
            raise BadRequest("Failed to retrieve devices")

    @trace_async
    async def upsert_device(self, data: DeviceCreate, locale: str = "en-US") -> DeviceOut:
        """Upsert device using raw SQL to avoid RLS race condition."""
        from ...utils.i18n import t

        if not data.user_id:
            raise BadRequest("User ID is required")

        try:
            tracking_context = domain_logger.operation_start("upsert_device", user_id=str(data.user_id), device_id=data.device_id, platform=data.platform, is_sandbox=data.is_sandbox)

            # Use raw SQL to avoid asyncpg prepared statement RLS race condition
            raw_sql = sa.text("""
                INSERT INTO devices (user_id, device_id, platform, push_token, app_version, os_version, device_model, locale, timezone, is_sandbox)
                VALUES (:user_id, :device_id, :platform, :push_token, :app_version, :os_version, :device_model, :locale, :timezone, :is_sandbox)
                ON CONFLICT (user_id, device_id) 
                DO UPDATE SET 
                    platform = EXCLUDED.platform,
                    push_token = EXCLUDED.push_token,
                    app_version = EXCLUDED.app_version,
                    os_version = EXCLUDED.os_version,
                    device_model = EXCLUDED.device_model,
                    locale = EXCLUDED.locale,
                    timezone = EXCLUDED.timezone,
                    is_sandbox = EXCLUDED.is_sandbox,
                    updated_at = now()
                RETURNING *;
            """)

            result = await self.session.execute(raw_sql, {
                "user_id": data.user_id,
                "device_id": data.device_id,
                "platform": data.platform,
                "push_token": data.push_token,
                "app_version": data.app_version,
                "os_version": data.os_version,
                "device_model": data.device_model,
                "locale": data.locale,
                "timezone": data.timezone,
                "is_sandbox": data.is_sandbox,
            })

            row = result.fetchone()
            if not row:
                raise BadRequest(t("device.error.registration_failed", locale=locale))

            device = DeviceOut.model_validate(row._asdict())

            domain_logger.operation_success(tracking_context, {
                "user_id": str(data.user_id),
                "device_id": data.device_id,
                "platform": data.platform,
                "device_uuid": str(device.id),
                "is_sandbox": data.is_sandbox
            })
            domain_logger.business_event("device_upserted", {
                "user_id": str(data.user_id),
                "device_id": data.device_id,
                "platform": data.platform,
                "device_uuid": str(device.id),
                "is_sandbox": data.is_sandbox,
                "operation": "upsert"
            })

            return device

        except IntegrityError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(data.user_id),
                "device_id": data.device_id,
                "platform": data.platform
            })
            logger.error("Device upsert integrity error", extra={
                "user_id": str(data.user_id), "device_id": data.device_id, "error": str(e)
            })
            raise Conflict(t("device.error.registration_failed", locale=locale))
        except sa.exc.SQLAlchemyError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(data.user_id),
                "device_id": data.device_id,
                "platform": data.platform
            })
            logger.error("Database error upserting device", extra={
                "user_id": str(data.user_id), "device_id": data.device_id, "error": str(e)
            })
            raise BadRequest(t("device.error.registration_failed", locale=locale))
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(data.user_id),
                "device_id": data.device_id,
                "platform": data.platform
            })
            logger.error("Unexpected error upserting device", extra={
                "user_id": str(data.user_id), "device_id": data.device_id, "error": str(e)
            })
            raise BadRequest(t("device.error.registration_failed", locale=locale))

    @trace_async
    async def update_device(self, device_id: UUID, data: DeviceUpdate) -> DeviceOut | None:
        """Update device by ID (RLS enforced)."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return cast(DeviceOut | None, await self.get_by_id(device_id))

        try:
            update_data['updated_at'] = sa.func.now()

            stmt = (
                sa.update(devices_table)
                .where(devices_table.c.id == device_id)
                .values(**update_data)
                .returning(devices_table)
            )

            result = await self.session.execute(stmt)
            row = result.fetchone()

            if not row:
                raise NotFound("Device not found or access denied")

            device_out: DeviceOut = DeviceOut.model_validate(row._asdict())
            return device_out

        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error updating device", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to update device")
        except Exception as e:
            logger.error("Unexpected error updating device", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to update device")

    @trace_async
    async def delete_device(self, device_id: UUID) -> None:
        """Delete device by ID (RLS enforced)."""
        try:
            tracking_context = domain_logger.operation_start("delete_device", device_id=str(device_id))

            stmt = sa.delete(devices_table).where(devices_table.c.id == device_id)

            result = await self.session.execute(stmt)
            if getattr(result, 'rowcount', 0) == 0:
                raise NotFound("Device not found or access denied")

            domain_logger.operation_success(tracking_context, {
                "device_id": str(device_id),
                "deleted": True
            })
            domain_logger.business_event("device_deleted", {
                "device_id": str(device_id),
                "operation": "delete_by_id"
            })

        except NotFound:
            domain_logger.operation_error(tracking_context, "Device not found", {
                "device_id": str(device_id)
            })
            raise
        except sa.exc.SQLAlchemyError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "device_id": str(device_id)
            })
            logger.error("Database error deleting device", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to delete device")
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "device_id": str(device_id)
            })
            logger.error("Unexpected error deleting device", extra={"device_id": str(device_id), "error": str(e)})
            raise BadRequest("Failed to delete device")

    @trace_async
    async def delete_user_device(self, user_id: UUID, device_id: str) -> None:
        """Delete device by user_id and device_id."""
        if not device_id.strip():
            raise BadRequest("Device ID cannot be empty")

        try:
            stmt = sa.delete(devices_table).where(
                sa.and_(
                    devices_table.c.user_id == user_id,
                    devices_table.c.device_id == device_id
                )
            )

            result = await self.session.execute(stmt)
            if getattr(result, 'rowcount', 0) == 0:
                raise NotFound("Device not found")

        except NotFound:
            raise
        except sa.exc.SQLAlchemyError as e:
            logger.error("Database error deleting user device", extra={
                "user_id": str(user_id), "device_id": device_id, "error": str(e)
            })
            raise BadRequest("Failed to delete device")
        except Exception as e:
            logger.error("Unexpected error deleting user device", extra={
                "user_id": str(user_id), "device_id": device_id, "error": str(e)
            })
            raise BadRequest("Failed to delete device")

    @trace_async
    async def get_push_tokens(self, user_id: UUID, platform: Platform | None = None) -> list[str]:
        """Get active push tokens for user, optionally filtered by platform."""
        try:
            tracking_context = domain_logger.operation_start("get_push_tokens", user_id=str(user_id), platform=str(platform) if platform else None)

            stmt = sa.select(devices_table.c.push_token).where(
                devices_table.c.user_id == user_id
            )

            if platform:
                # Use text comparison with explicit cast in SQL
                stmt = stmt.where(sa.text("devices.platform::text = :platform")).params(platform=platform)

            result = await self.session.execute(stmt)
            tokens = [row.push_token for row in result.fetchall() if row.push_token]

            domain_logger.operation_success(tracking_context, {
                "user_id": str(user_id),
                "platform": str(platform) if platform else None,
                "token_count": len(tokens)
            })

            logger.info("Retrieved push tokens", extra={
                "user_id": str(user_id), "platform": platform, "token_count": len(tokens)
            })

            return tokens

        except sa.exc.SQLAlchemyError as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id),
                "platform": str(platform) if platform else None
            })
            logger.error("Database error getting push tokens", extra={
                "user_id": str(user_id), "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to retrieve push tokens")
        except Exception as e:
            domain_logger.operation_error(tracking_context, str(e), {
                "user_id": str(user_id),
                "platform": str(platform) if platform else None
            })
            logger.error("Unexpected error getting push tokens", extra={
                "user_id": str(user_id), "platform": platform, "error": str(e)
            })
            raise BadRequest("Failed to retrieve push tokens")
