"""Analytics service for KPI calculations and reporting."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...db.uow import async_uow_factory
from ...utils.clock import utcnow
from ...utils.errors import BadRequest
from ...utils.i18n import t
from ...utils.tracing import trace_async
from .cache import AnalyticsCache
from .repository import AnalyticsRepository
from .schemas import AnalyticsResponse, KPIOut, KPIUser30DOut


class AnalyticsService:
    """Service for analytics calculations and KPI reporting."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        redis_client: Redis | None = None
    ):
        self.session_factory = session_factory
        self.cache = AnalyticsCache(redis_client) if redis_client else None

    @trace_async
    async def get_user_kpi_30d(self, user_id: UUID) -> KPIUser30DOut | None:
        """Get 30-day KPI for user."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)
            result: KPIUser30DOut | None = await repository.get_user_kpi_30d(user_id)
            return result

    @trace_async
    async def get_communication_insights(self, user_id: UUID, days: int = 7, timezone: str | None = None) -> AnalyticsResponse:
        """Get communication insights and engagement metrics."""
        if not (1 <= days <= 365):
            raise BadRequest("Days must be between 1 and 365")

        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)

            insights = await repository.get_communication_insights(user_id, days)

            kpis = []

            # Response Rate
            response_rate = insights.get('response_rate', 0)
            kpis.append(KPIOut(
                id="response_rate_insights",
                name="analytics.response_rate",
                value=f"{response_rate}%",
                unit="percent",
                trend="up" if response_rate >= 70 else "down",
                metadata={
                    "message": "analytics.response_rate_message",
                    "benchmark": 70,
                    "status": "good" if response_rate >= 70 else "needs_improvement"
                }
            ))

            # Average Response Time
            avg_hours = insights.get('avg_response_hours', 0)
            kpis.append(KPIOut(
                id="avg_response_time_insights",
                name="analytics.avg_response_time",
                value=f"{avg_hours}h",
                unit="hours",
                trend="stable",
                metadata={
                    "message": "analytics.avg_response_time_message",
                    "benchmark": 2.0,
                    "status": "good" if avg_hours <= 2.0 else "needs_improvement"
                }
            ))

            # Active Conversations
            current_active = insights.get('current_active_conversations', 0)
            prev_active = insights.get('prev_active_conversations', 0)
            kpis.append(KPIOut(
                id="active_conversations_insights",
                name="analytics.active_conversations",
                value=current_active,
                unit="conversations",
                trend=self._calculate_trend(current_active, prev_active),
                metadata={
                    "message": "analytics.active_conversations_message",
                    "change": current_active - prev_active,
                    "previous_period": prev_active
                }
            ))

            # AI Usage
            ai_total = insights.get('ai_total_requests', 0)
            ai_successful = insights.get('ai_successful_requests', 0)
            ai_success_rate = round((ai_successful / ai_total * 100), 0) if ai_total > 0 else 0
            kpis.append(KPIOut(
                id="ai_usage_insights",
                name="analytics.ai_usage",
                value=f"{ai_success_rate}%",
                unit="percent",
                trend="up" if ai_success_rate >= 80 else "stable",
                metadata={
                    "message": "analytics.ai_usage_message",
                    "total_requests": ai_total,
                    "successful_requests": ai_successful
                }
            ))

            # Best Day
            best_day = insights.get('best_day_name', 'unknown')
            best_day_activity = insights.get('best_day_activity', 0)
            kpis.append(KPIOut(
                id="best_day_insights",
                name="analytics.best_day",
                value=f"analytics.days.{best_day}",
                unit="day",
                trend="stable",
                metadata={
                    "message": "analytics.best_day_message",
                    "activity_count": best_day_activity
                }
            ))

            return AnalyticsResponse(
                kpis=kpis,
                period=f"{days}d",
                metadata={
                    "user_id": str(user_id),
                    "calculated_at": utcnow().isoformat(),
                    "timezone": timezone,
                    "type": "communication_insights"
                }
            )

    @trace_async
    async def get_user_analytics(self, user_id: UUID, days: int = 30, timezone: str | None = None, locale: str = "en-US", channel: str | None = None) -> AnalyticsResponse:
        """Get comprehensive user analytics."""
        if not (1 <= days <= 365):
            raise BadRequest("Days must be between 1 and 365")

        from ...utils.i18n import clear_translation_cache, t
        from ...utils.logging import get_safe_logger

        logger = get_safe_logger(__name__)

        # Check cache first (only for 30-day overview)
        if self.cache and days == 30 and channel is None:
            cached = await self.cache.get_overview(user_id)
            if cached:
                logger.info("Analytics overview served from cache", extra={
                    "user_id": str(user_id)
                })
                # Reconstruct AnalyticsResponse from cached dict
                return AnalyticsResponse(**cached)

        # Clear cache to ensure fresh translations
        clear_translation_cache()

        # Use separate sessions to avoid transaction conflicts
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow1:
            repository1 = AnalyticsRepository(uow1.session)
            insights = await repository1.get_communication_insights(user_id, days, channel)

        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow2:
            repository2 = AnalyticsRepository(uow2.session)
            chart_data = await repository2.get_weekly_activity_chart(user_id, days, locale, channel)

        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow3:
            repository3 = AnalyticsRepository(uow3.session)
            current_activity = await repository3.get_user_activity_summary(user_id, days, channel=channel)

        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow4:
            repository4 = AnalyticsRepository(uow4.session)
            previous_activity = await repository4.get_user_activity_summary(user_id, days, offset_days=days, channel=channel)

            kpis = []

            # Communication Insights (new)
            response_rate = insights.get('response_rate', 0)
            kpis.append(KPIOut(
                id="response_rate",
                name=t("analytics.response_rate", locale=locale),
                value=response_rate,
                unit="percent",
                trend="up" if response_rate >= 70 else "down",
                metadata={
                    "message": t("analytics.response_rate_message", response_rate=response_rate, locale=locale),
                    "benchmark": 70
                }
            ))

            avg_hours = insights.get('avg_response_hours', 0)
            kpis.append(KPIOut(
                id="avg_response_time_overview",
                name=t("analytics.avg_response_time", locale=locale),
                value=avg_hours,
                unit="hours",
                trend="stable",
                metadata={
                    "message": t("analytics.avg_response_time_message", avg_hours=avg_hours, locale=locale),
                    "benchmark": 2.0
                }
            ))

            current_active = insights.get('current_active_conversations', 0)
            prev_active = insights.get('prev_active_conversations', 0)
            kpis.append(KPIOut(
                id="active_conversations",
                name=t("analytics.active_conversations", locale=locale),
                value=current_active,
                unit="conversations",
                trend=self._calculate_trend(current_active, prev_active),
                metadata={
                    "message": t("analytics.active_conversations_message", current=current_active, previous=prev_active, locale=locale),
                    "change": current_active - prev_active
                }
            ))

            ai_total = insights.get('ai_total_requests', 0)
            ai_successful = insights.get('ai_successful_requests', 0)
            ai_success_rate = round((ai_successful / ai_total * 100), 0) if ai_total > 0 else 0
            kpis.append(KPIOut(
                id="ai_usage",
                name=t("analytics.ai_usage", locale=locale),
                value=ai_success_rate,
                unit="percent",
                trend="up" if ai_success_rate >= 80 else "stable",
                metadata={
                    "message": t("analytics.ai_usage_message", total=ai_total, success_rate=ai_success_rate, locale=locale),
                    "total_requests": ai_total
                }
            ))

            # Translate day names directly
            best_day_key = insights.get('best_day_name', 'unknown')
            best_day_translated = t(f"analytics.days.{best_day_key}", locale=locale)

            kpis.append(KPIOut(
                id="best_day",
                name=t("analytics.best_day", locale=locale),
                value=f"analytics.days.{best_day_key}",
                unit="day",
                trend="stable",
                metadata={
                    "message": t("analytics.best_day_message", day=best_day_translated, locale=locale)
                }
            ))

            # Original KPIs
            threads_current = current_activity.get("active_threads", 0)
            threads_previous = previous_activity.get("active_threads", 0)
            threads_trend = self._calculate_trend(threads_current, threads_previous)
            kpis.append(KPIOut(
                id="active_threads",
                name="analytics.active_threads",
                value=threads_current,
                unit="threads",
                trend=threads_trend,
                metadata={
                    "previous_period": threads_previous,
                    "change": threads_current - threads_previous,
                    "change_percent": self._calculate_percent_change(threads_current, threads_previous)
                }
            ))

            sent_current = current_activity.get("messages_sent", 0)
            sent_previous = previous_activity.get("messages_sent", 0)
            sent_trend = self._calculate_trend(sent_current, sent_previous)
            kpis.append(KPIOut(
                id="messages_sent",
                name="analytics.messages_sent",
                value=sent_current,
                unit="messages",
                trend=sent_trend,
                metadata={
                    "previous_period": sent_previous,
                    "change": sent_current - sent_previous,
                    "change_percent": self._calculate_percent_change(sent_current, sent_previous),
                    "daily_average": round(sent_current / days, 1) if days > 0 else 0
                }
            ))

        result = AnalyticsResponse(
            kpis=kpis,
            period=f"{days}d",
            metadata={
                "user_id": str(user_id),
                "calculated_at": utcnow().isoformat(),
                "timezone": timezone,
                "comparison_period": f"previous_{days}d",
                "type": "comprehensive_analytics",
                "chart_data": chart_data
            }
        )

        # Cache result (only for 30-day overview)
        if self.cache and days == 30 and channel is None:
            await self.cache.set_overview(user_id, result.model_dump())

        return result

    @trace_async
    async def get_thread_metrics(self, user_id: UUID, thread_id: UUID, user_timezone: str | None = None, locale: str = "en-US") -> AnalyticsResponse:
        """Get contextual metrics for a specific thread."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)

            # Verify thread exists and belongs to user
            thread_exists = await repository.verify_thread_access(user_id, thread_id)
            if not thread_exists:
                from ...utils.errors import NotFound
                raise NotFound(f"Thread {thread_id} not found or access denied")

            # Get thread insights
            insights = await repository.get_thread_insights(thread_id)
            if not insights:
                raise NotFound(f"No data found for thread {thread_id}")

            # Get locale for translations (passed from API)
            # locale parameter is already available

            # Build contextual KPIs
            kpis = []

            # Days conversing
            kpis.append(KPIOut(
                id="days_conversing",
                name=t("analytics.days_conversing", locale=locale),
                value=insights['days_conversing'],
                unit="days",
                trend="stable",
                metadata={
                    "message": t("analytics.days_conversing_message",
                               days=insights['days_conversing'], locale=locale),
                    "first_message": insights.get('first_message_at')
                }
            ))

            # Total messages exchanged
            kpis.append(KPIOut(
                id="total_messages",
                name=t("analytics.total_messages_exchanged", locale=locale),
                value=insights['total_messages'],
                unit="messages",
                trend="stable",
                metadata={
                    "message": t("analytics.total_messages_exchanged_message",
                               total=insights['total_messages'], locale=locale),
                    "user_messages": insights['user_messages'],
                    "contact_messages": insights['contact_messages']
                }
            ))

            # Conversation balance
            if insights['total_messages'] > 0:
                kpis.append(KPIOut(
                    id="conversation_balance",
                    name=t("analytics.conversation_balance", locale=locale),
                    value=f"{insights['user_percentage']}% / {insights['contact_percentage']}%",
                    unit="balance",
                    trend="stable",
                    metadata={
                        "message": t("analytics.conversation_balance_message",
                                   user_percentage=insights['user_percentage'],
                                   contact_percentage=insights['contact_percentage'], locale=locale),
                        "user_percentage": insights['user_percentage'],
                        "contact_percentage": insights['contact_percentage']
                    }
                ))

            # Response time
            if insights['avg_response_hours'] > 0:
                kpis.append(KPIOut(
                    id="avg_response_time",
                    name=t("analytics.avg_response_time", locale=locale),
                    value=insights['avg_response_hours'],
                    unit="hours",
                    trend="stable",
                    metadata={
                        "message": t("analytics.avg_response_time_thread_message",
                                   hours=insights['avg_response_hours'], locale=locale)
                    }
                ))

            # Most active hour
            if insights['most_active_hour'] is not None:
                kpis.append(KPIOut(
                    id="most_active_hour",
                    name=t("analytics.most_active_hour", locale=locale),
                    value=f"{insights['most_active_hour']:02d}:00",
                    unit="hour",
                    trend="stable",
                    metadata={
                        "message": t("analytics.most_active_hour_message",
                                   hour=f"{insights['most_active_hour']:02d}:00", locale=locale),
                        "hour": insights['most_active_hour']
                    }
                ))

            # AI assistance
            if insights['total_ai_jobs'] > 0:
                kpis.append(KPIOut(
                    id="ai_assistance",
                    name=t("analytics.ai_assistance", locale=locale),
                    value=insights['total_ai_jobs'],
                    unit="jobs",
                    trend="stable",
                    metadata={
                        "message": t("analytics.ai_assistance_message",
                                   suggestions=insights['suggestions_used'],
                                   icebreakers=insights['icebreakers_created'], locale=locale),
                        "suggestions_used": insights['suggestions_used'],
                        "icebreakers_created": insights['icebreakers_created'],
                        "completed_jobs": insights['completed_ai_jobs']
                    }
                ))

            # Conversation status
            now = datetime.now(UTC)
            last_activity = insights.get('last_activity')
            if last_activity:
                # Ensure last_activity is timezone-aware
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=UTC)
                hours_since_activity = (now - last_activity).total_seconds() / 3600
                if hours_since_activity < 24:
                    status = t("analytics.conversation_active", locale=locale)
                    trend = "up"
                elif hours_since_activity < 72:
                    status = t("analytics.conversation_recent", locale=locale)
                    trend = "stable"
                else:
                    status = t("analytics.conversation_inactive", locale=locale)
                    trend = "down"

                kpis.append(KPIOut(
                    id="conversation_status",
                    name=t("analytics.conversation_status", locale=locale),
                    value=status,
                    unit="status",
                    trend=trend,
                    metadata={
                        "last_activity": last_activity,
                        "hours_since_activity": round(hours_since_activity, 1)
                    }
                ))

            return AnalyticsResponse(
                kpis=kpis,
                period="thread_lifetime",
                metadata={
                    "thread_id": str(thread_id),
                    "channel": insights.get('channel'),
                    "calculated_at": datetime.now(UTC),
                    "timezone": user_timezone,
                    "type": "thread_insights"
                }
            )

    @trace_async
    async def get_system_analytics(self, days: int = 1) -> AnalyticsResponse:
        """Get system-wide analytics."""
        if not (1 <= days <= 365):
            raise BadRequest("Days must be between 1 and 365")

        # System analytics don't need user_id for RLS
        async with async_uow_factory(self.session_factory)() as uow:
            repository = AnalyticsRepository(uow.session)

            since = utcnow() - timedelta(days=days)
            metrics = await repository.get_system_metrics(since)

            kpis = [
                KPIOut(id="total_users", name="analytics.total_users", value=metrics.get("total_users", 0), unit="users", trend=None),
                KPIOut(id="new_users", name="analytics.new_users", value=metrics.get("new_users", 0), unit="users", trend=None),
                KPIOut(id="total_messages", name="analytics.total_messages", value=metrics.get("total_messages", 0), unit="messages", trend=None),
                KPIOut(id="recent_messages", name="analytics.recent_messages", value=metrics.get("recent_messages", 0), unit="messages", trend=None),
                KPIOut(id="ai_jobs", name="analytics.ai_jobs", value=metrics.get("recent_ai_jobs", 0), unit="jobs", trend=None),
                KPIOut(id="completed_ai_jobs", name="analytics.completed_ai_jobs", value=metrics.get("completed_ai_jobs", 0), unit="jobs", trend=None),
            ]

            return AnalyticsResponse(
                kpis=kpis,
                period=f"{days}d",
                metadata=metrics
            )

    @trace_async
    async def get_channel_analytics(self, days: int = 30) -> AnalyticsResponse:
        """Get channel usage analytics."""
        if not (1 <= days <= 365):
            raise BadRequest("Days must be between 1 and 365")

        # Channel analytics don't need user_id for RLS
        async with async_uow_factory(self.session_factory)() as uow:
            repository = AnalyticsRepository(uow.session)

            channel_stats = await repository.get_channel_stats(days)

            kpis = [
                KPIOut(id=f"{channel}_threads", name=f"analytics.channels.{channel}_threads", value=count, unit="threads", trend=None)
                for channel, count in channel_stats.items()
            ]

            return AnalyticsResponse(
                kpis=kpis,
                period=f"{days}d",
                metadata={"type": "channel_stats", "calculated_at": utcnow().isoformat()}
            )

    @trace_async
    async def get_onboarding_analytics(self) -> AnalyticsResponse:
        """Get onboarding funnel analytics."""
        # Onboarding analytics don't need user_id for RLS
        async with async_uow_factory(self.session_factory)() as uow:
            repository = AnalyticsRepository(uow.session)

            funnel_data = await repository.get_onboarding_funnel()

            kpis = [
                KPIOut(id=f"{step}_completed", name=f"analytics.onboarding.{step}_completed", value=count, unit="users", trend=None)
                for step, count in funnel_data.items()
            ]

            return AnalyticsResponse(
                kpis=kpis,
                period="all_time",
                metadata={"type": "onboarding_funnel", "calculated_at": utcnow().isoformat()}
            )

    @trace_async
    async def calculate_engagement_score(self, user_id: UUID) -> float:
        """Calculate user engagement score (0-100)."""
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)

            activity = await repository.get_user_activity_summary(user_id, 30)

            # Simple engagement scoring
            threads_score = min(activity.get("active_threads", 0) * 10, 40)  # Max 40 points
            messages_score = min(activity.get("messages_sent", 0) * 2, 30)   # Max 30 points
            ai_score = min(activity.get("ai_jobs_completed", 0) * 5, 30)     # Max 30 points

            return cast(float, min(threads_score + messages_score + ai_score, 100.0))

    @trace_async
    async def get_thread_analytics_tier1(self, user_id: UUID, thread_id: UUID) -> dict[str, Any]:
        """Get comprehensive TIER 1 analytics for a thread."""
        from ...utils.errors import NotFound
        from ...utils.logging import get_safe_logger

        logger = get_safe_logger(__name__)

        # Check cache first
        if self.cache:
            cached = await self.cache.get_tier1(user_id, thread_id)
            if cached:
                logger.info("Analytics TIER 1 served from cache", extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id)
                })
                return cached

        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)

            # Verify thread access
            has_access = await repository.verify_thread_access(user_id, thread_id)
            if not has_access:
                raise NotFound(f"Thread {thread_id} not found or access denied")

            # Fetch all TIER 1 metrics (8 queries executed within same session)
            # Note: These run sequentially but share the same DB connection,
            # minimizing overhead. Each query is optimized with indexes (migration 037).
            # Total execution time: ~400ms uncached, ~200ms cached
            message_balance = await repository.get_thread_message_balance(thread_id)
            response_times = await repository.get_thread_response_times(thread_id)
            response_trend = await repository.get_thread_response_trend(thread_id)
            conversation_depth = await repository.get_thread_depth_normalized(thread_id)
            recency = await repository.get_thread_recency(thread_id)
            message_length_context = await repository.get_message_length_context(thread_id)
            emoji_usage = await repository.get_emoji_usage(thread_id)
            contact_responsiveness = await repository.get_contact_responsiveness(thread_id)

            result = {
                'thread_id': str(thread_id),
                'message_balance': message_balance,
                'response_times': response_times,
                'response_trend': response_trend,
                'conversation_depth': conversation_depth,
                'recency': recency,
                'message_length_context': message_length_context,
                'emoji_usage': emoji_usage,
                'contact_responsiveness': contact_responsiveness,
                'calculated_at': utcnow().isoformat()
            }

            # Cache with dynamic TTL based on thread activity
            if self.cache:
                last_activity = recency.get('last_activity')
                if last_activity:
                    # Ensure last_activity is timezone-aware
                    if last_activity.tzinfo is None:
                        last_activity = last_activity.replace(tzinfo=UTC)
                    last_activity_hours = int((utcnow() - last_activity).total_seconds() / 3600)
                else:
                    last_activity_hours = None
                await self.cache.set_tier1(user_id, thread_id, result, last_activity_hours)

            return result

    def _calculate_trend(self, current: int, previous: int) -> str:
        """Calculate trend direction based on current vs previous values."""
        if current > previous:
            return "up"
        elif current < previous:
            return "down"
        else:
            return "stable"

    def _calculate_percent_change(self, current: int, previous: int) -> float:
        """Calculate percentage change between current and previous values."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    @trace_async
    async def get_thread_analytics_tier2(
        self,
        user_id: UUID,
        thread_id: UUID,
        bedrock_client: Any = None,
        ai_cache: Any = None
    ) -> dict[str, Any]:
        """
        Get comprehensive TIER 2 analytics for a thread (TIER 1 + AI analysis).
        
        Args:
            user_id: User ID for RLS
            thread_id: Thread ID to analyze
            bedrock_client: Optional BedrockClient instance
            ai_cache: Optional AICache instance
            
        Returns:
            Dictionary with TIER 1 + TIER 2 metrics
        """
        from ..ai.bedrock_client import BedrockClient
        from ..ai.cache import AICache
        from ..ai.conversation_analyzer import ConversationAnalyzer
        from ...utils.logging import get_safe_logger
        from .scoring import calculate_connection_score

        logger = get_safe_logger(__name__)

        # Check cache first
        if self.cache:
            cached = await self.cache.get_tier2(user_id, thread_id)
            if cached:
                logger.info("Analytics TIER 2 served from cache", extra={
                    "user_id": str(user_id),
                    "thread_id": str(thread_id)
                })
                return cached

        # Get TIER 1 metrics first
        tier1_metrics = await self.get_thread_analytics_tier1(user_id, thread_id)

        # Initialize AI components if not provided
        if bedrock_client is None:
            bedrock_client = BedrockClient()
        if ai_cache is None:
            ai_cache = AICache()

        analyzer = ConversationAnalyzer(bedrock_client, ai_cache)

        # Fetch recent messages for AI analysis
        async with async_uow_factory(self.session_factory, user_id=str(user_id))() as uow:
            repository = AnalyticsRepository(uow.session)
            messages = await repository.get_thread_messages_for_analysis(thread_id, limit=20)

        # Run AI analyses in parallel (but sequentially for now to avoid rate limits)
        interest = await analyzer.analyze_interest(messages, thread_id)
        sentiment = await analyzer.analyze_sentiment(messages, thread_id)
        stage = await analyzer.detect_conversation_stage(messages, thread_id)
        question_rate = await analyzer.analyze_question_rate(messages, thread_id)

        # Build AI analysis object
        ai_analysis = {
            'interest': interest,
            'sentiment': sentiment,
            'stage': stage,
            'question_rate': question_rate,
            'recommendations': []
        }

        # Generate recommendations based on all metrics
        recommendations = await analyzer.generate_recommendations(
            tier1_metrics,
            messages,
            thread_id
        )
        ai_analysis['recommendations'] = recommendations

        # Calculate connection score
        combined_metrics = {
            **tier1_metrics,
            'ai_analysis': ai_analysis
        }
        connection_score = calculate_connection_score(combined_metrics)

        # Return complete TIER 2 analytics
        result = {
            **tier1_metrics,
            'ai_analysis': ai_analysis,
            'connection_score': connection_score
        }

        # Cache result
        if self.cache:
            await self.cache.set_tier2(user_id, thread_id, result)

        return result


def create_analytics_service(session_factory: async_sessionmaker[AsyncSession]) -> AnalyticsService:
    """Factory function for AnalyticsService."""
    return AnalyticsService(session_factory)
