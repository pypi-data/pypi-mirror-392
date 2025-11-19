"""Background task for daily quota reset and cleanup."""

import asyncio
from datetime import datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...utils.clock import utcnow
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from .quota_service import create_quota_service
from .service import create_subscription_service

logger = get_logger(__name__)


class QuotaResetTask:
    """Background task for daily quota reset and cleanup."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        reset_time: time = time(0, 0, 0),  # Midnight UTC
        cleanup_days: int = 7
    ):
        self.session_factory = session_factory
        self.reset_time = reset_time
        self.cleanup_days = cleanup_days
        self.running = False
        self._task: asyncio.Task | None = None

        # Create services
        self.subscription_service = create_subscription_service(session_factory)
        self.quota_service = create_quota_service(session_factory, self.subscription_service)

    @trace_async
    async def start(self) -> None:
        """Start the quota reset task scheduler."""
        if self.running:
            logger.warning("Quota reset task is already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_scheduler())

        logger.info("Quota reset task scheduler started", extra={
            "reset_time": self.reset_time.isoformat(),
            "cleanup_days": self.cleanup_days
        })

    async def stop(self) -> None:
        """Stop the quota reset task scheduler."""
        if not self.running:
            return

        self.running = False

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Quota reset task scheduler stopped")

    async def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        logger.info("Quota reset scheduler started")

        while self.running:
            try:
                # Calculate next reset time
                next_reset = self._get_next_reset_time()
                now = utcnow()

                # Calculate sleep duration
                sleep_duration = (next_reset - now).total_seconds()

                if sleep_duration > 0:
                    logger.info("Waiting for next quota reset", extra={
                        "next_reset": next_reset.isoformat(),
                        "sleep_duration_seconds": sleep_duration
                    })

                    # Sleep until next reset time
                    await asyncio.sleep(sleep_duration)

                if not self.running:
                    break

                # Perform quota reset
                await self._perform_quota_reset()

                # Perform cleanup (weekly)
                if now.weekday() == 0:  # Monday
                    await self._perform_quota_cleanup()

            except asyncio.CancelledError:
                logger.info("Quota reset scheduler cancelled")
                break
            except Exception as e:
                logger.error("Error in quota reset scheduler", extra={
                    "error": str(e)
                })
                # Sleep for 1 hour before retrying
                await asyncio.sleep(3600)

    @trace_async
    async def _perform_quota_reset(self) -> None:
        """Perform the daily quota reset."""
        try:
            logger.info("Starting daily quota reset")

            reset_count = await self.quota_service.reset_daily_quotas()

            logger.info("Daily quota reset completed", extra={
                "reset_count": reset_count,
                "timestamp": utcnow().isoformat()
            })

        except Exception as e:
            logger.error("Failed to perform daily quota reset", extra={
                "error": str(e)
            })

    @trace_async
    async def _perform_quota_cleanup(self) -> None:
        """Perform weekly quota data cleanup."""
        try:
            logger.info("Starting weekly quota cleanup")

            cleanup_count = await self.quota_service.cleanup_expired_quota_data(
                days_to_keep=self.cleanup_days
            )

            logger.info("Weekly quota cleanup completed", extra={
                "cleanup_count": cleanup_count,
                "days_kept": self.cleanup_days,
                "timestamp": utcnow().isoformat()
            })

        except Exception as e:
            logger.error("Failed to perform quota cleanup", extra={
                "error": str(e)
            })

    def _get_next_reset_time(self) -> datetime:
        """Calculate the next quota reset time."""
        now = utcnow()
        today_reset = datetime.combine(now.date(), self.reset_time).replace(tzinfo=now.tzinfo)

        if now >= today_reset:
            # Next reset is tomorrow
            tomorrow = now.date() + timedelta(days=1)
            return datetime.combine(tomorrow, self.reset_time).replace(tzinfo=now.tzinfo)
        else:
            # Next reset is today
            return today_reset

    @trace_async
    async def run_manual_reset(self) -> dict:
        """Run manual quota reset (for testing/admin purposes)."""
        try:
            logger.info("Starting manual quota reset")

            reset_count = await self.quota_service.reset_daily_quotas()
            cleanup_count = await self.quota_service.cleanup_expired_quota_data(
                days_to_keep=self.cleanup_days
            )

            result = {
                "reset_count": reset_count,
                "cleanup_count": cleanup_count,
                "timestamp": utcnow().isoformat(),
                "manual": True
            }

            logger.info("Manual quota reset completed", extra=result)

            return result

        except Exception as e:
            logger.error("Failed to perform manual quota reset", extra={
                "error": str(e)
            })
            raise

    @trace_async
    async def get_next_reset_info(self) -> dict:
        """Get information about the next scheduled reset."""
        next_reset = self._get_next_reset_time()
        now = utcnow()

        return {
            "next_reset_time": next_reset.isoformat(),
            "current_time": now.isoformat(),
            "seconds_until_reset": int((next_reset - now).total_seconds()),
            "is_running": self.running,
            "reset_time_utc": self.reset_time.isoformat(),
            "cleanup_days": self.cleanup_days
        }


def create_quota_reset_task(
    session_factory: async_sessionmaker[AsyncSession],
    reset_time: time = time(0, 0, 0),
    cleanup_days: int = 7
) -> QuotaResetTask:
    """Factory function for QuotaResetTask."""
    return QuotaResetTask(session_factory, reset_time, cleanup_days)
