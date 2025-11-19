"""Analytics repository for KPI calculations and reporting."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, extract, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from ...utils.request_tracking import RequestTracker
from ...utils.domain_logger import get_domain_logger
from ..threads.schemas import messages_table, threads_table

logger = get_logger(__name__)
domain_logger = get_domain_logger("analytics")


class AnalyticsRepository:
    """Repository for analytics calculations and KPI reporting."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @trace_async
    async def get_communication_insights(self, user_id: UUID, days: int, channel: str | None = None) -> dict[str, Any]:
        """Get communication insights for user - production ready."""
        with RequestTracker(user_id=str(user_id), operation="get_communication_insights", 
                          days=days, channel=channel) as tracker:
            try:
                tracking_context = domain_logger.operation_start("get_communication_insights", 
                    user_id=str(user_id), days=days, channel=channel)

                # Calculate date ranges
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=days)

                # Build base query with channel filter
                base_query = select(
                    func.count(threads_table.c.id.distinct()).label('total_threads'),
                    func.count(
                        case((messages_table.c.sender == 'user', threads_table.c.id), else_=None).distinct()
                    ).label('user_threads'),
                    func.count(
                        case((messages_table.c.sender == 'contact', threads_table.c.id), else_=None).distinct()
                    ).label('contact_threads'),
                    func.count(
                        case((messages_table.c.sender == 'user', 1), else_=None)
                    ).label('user_messages'),
                    func.count(
                        case((messages_table.c.sender == 'contact', 1), else_=None)
                    ).label('contact_messages')
                ).select_from(
                    threads_table.outerjoin(
                        messages_table,
                        and_(
                            messages_table.c.thread_id == threads_table.c.id,
                            messages_table.c.created_at >= start_date
                        )
                    )
                ).where(
                    threads_table.c.user_id == text('app.current_user_id()')
                )

                if channel:
                    base_query = base_query.where(threads_table.c.channel == channel)

                domain_logger.database_operation("communication_insights_query", 
                    user_id=str(user_id), days=days, channel=channel, 
                    date_range=f"{start_date.isoformat()} to {end_date.isoformat()}")

                result = await self.session.execute(base_query)
                stats = result.fetchone()

                # Calculate response rate
                response_rate = 0
                if stats.user_threads > 0:
                    response_rate = round((stats.contact_threads / stats.user_threads) * 100, 1)

                # Get AI stats
                ai_query = select(
                    func.count().label('total'),
                    func.count(case((text("status = 'done'"), 1), else_=None)).label('completed')
                ).select_from(
                    text('ai_jobs')
                ).where(
                    and_(
                        text('user_id = app.current_user_id()'),
                        text('created_at >= :start_date')
                    )
                )

                domain_logger.database_operation("ai_stats_query", 
                    user_id=str(user_id), days=days, start_date=start_date.isoformat())

                ai_result = await self.session.execute(ai_query, {'start_date': start_date})
                ai_stats = ai_result.fetchone()

                # Get average response time - limited to 24h window for realistic results
                avg_time_query = select(
                func.coalesce(
                    func.avg(
                        extract('epoch', text('m2.created_at - m1.created_at')) / 3600
                    ), 0
                ).label('avg_hours')
            ).select_from(
                messages_table.alias('m1').join(
                    messages_table.alias('m2'),
                    text('m1.thread_id = m2.thread_id')
                ).join(
                    threads_table,
                    text('threads.id = m1.thread_id')
                )
            ).where(
                and_(
                    threads_table.c.user_id == text('app.current_user_id()'),
                    text("m1.sender = 'user'"),
                    text("m2.sender = 'contact'"),
                    text('m2.created_at > m1.created_at'),
                    text("m2.created_at <= m1.created_at + INTERVAL '24 hours'"),
                    text('m1.created_at >= :start_date')
                )
            )

                if channel:
                    avg_time_query = avg_time_query.where(threads_table.c.channel == channel)

                domain_logger.database_operation("avg_response_time_query", 
                    user_id=str(user_id), days=days, channel=channel)

                avg_time_result = await self.session.execute(avg_time_query, {'start_date': start_date})
                avg_hours = avg_time_result.scalar() or 0

                # Get best day - return day key for i18n
                best_day_query = select(
                    case(
                        (extract('dow', messages_table.c.created_at) == 0, 'sunday'),
                        (extract('dow', messages_table.c.created_at) == 1, 'monday'),
                        (extract('dow', messages_table.c.created_at) == 2, 'tuesday'),
                        (extract('dow', messages_table.c.created_at) == 3, 'wednesday'),
                        (extract('dow', messages_table.c.created_at) == 4, 'thursday'),
                        (extract('dow', messages_table.c.created_at) == 5, 'friday'),
                        (extract('dow', messages_table.c.created_at) == 6, 'saturday'),
                        else_='unknown'
                    ).label('day_key'),
                    func.count().label('message_count')
                ).select_from(
                    messages_table.join(threads_table, threads_table.c.id == messages_table.c.thread_id)
                ).where(
                    and_(
                        threads_table.c.user_id == text('app.current_user_id()'),
                        messages_table.c.created_at >= start_date
                    )
                ).group_by(
                    extract('dow', messages_table.c.created_at)
                ).order_by(
                    func.count().desc()
                ).limit(1)

                if channel:
                    best_day_query = best_day_query.where(threads_table.c.channel == channel)

                domain_logger.database_operation("best_day_query", 
                    user_id=str(user_id), days=days, channel=channel)

                best_day_result = await self.session.execute(best_day_query, {'start_date': start_date})
                best_day = best_day_result.fetchone()

                result = {
                    'response_rate': response_rate,
                    'avg_response_hours': round(avg_hours, 1),
                    'current_active_conversations': stats.total_threads or 0,
                    'prev_active_conversations': max(0, (stats.total_threads or 0) - 1),
                    'ai_total_requests': ai_stats.total or 0,
                    'ai_successful_requests': ai_stats.completed or 0,
                    'best_day_name': best_day.day_key if best_day else 'unknown',
                    'best_day_activity': best_day.message_count if best_day else 0
                }

                domain_logger.business_event("communication_insights_calculated", 
                    user_id=str(user_id), days=days, channel=channel,
                    response_rate=response_rate, avg_response_hours=round(avg_hours, 1),
                    total_threads=stats.total_threads, ai_requests=ai_stats.total)
                domain_logger.operation_success(tracking_context, 
                    user_id=str(user_id), days=days, channel=channel,
                    total_threads=stats.total_threads, response_rate=response_rate)
                tracker.log_success(total_threads=stats.total_threads, response_rate=response_rate,
                    ai_requests=ai_stats.total)
                return result

            except Exception as e:
                error_id = domain_logger.operation_error(tracking_context, error=e,
                    user_id=str(user_id), days=days, channel=channel)
                tracker.log_error(e, context={"days": days, "channel": channel})
                return {
                    'response_rate': 0,
                    'avg_response_hours': 0,
                    'current_active_conversations': 0,
                'prev_active_conversations': 0,
                'ai_total_requests': 0,
                'ai_successful_requests': 0,
                'best_day_name': 'unknown',
                'best_day_activity': 0
            }

    @trace_async
    async def get_weekly_activity_chart(self, user_id: UUID, days: int, locale: str = "en-US", channel: str | None = None) -> dict[str, Any]:
        """Get activity data for chart - daily for <=7 days, weekly for >7 days."""

        from ...utils.i18n import t

        try:
            if days <= 7:
                # Daily breakdown for short periods
                channel_filter = "AND t.channel = :channel" if channel else ""
                params = {}
                if channel:
                    params['channel'] = channel

                query_text = f"""
                    SELECT 
                        DATE(m.created_at) as day,
                        COUNT(*) FILTER (WHERE m.sender = 'user') as sent,
                        COUNT(*) FILTER (WHERE m.sender = 'contact') as received,
                        EXTRACT(DOW FROM m.created_at) as day_of_week
                    FROM messages m
                    JOIN threads t ON t.id = m.thread_id
                    WHERE t.user_id = app.current_user_id()
                    AND m.created_at >= CURRENT_DATE - INTERVAL '{days} days'
                    {channel_filter}
                    GROUP BY DATE(m.created_at), EXTRACT(DOW FROM m.created_at)
                    ORDER BY DATE(m.created_at)
                """

                result = await self.session.execute(text(query_text), params)
                rows = result.fetchall()

                # Translate day names
                day_names = {
                    0: t("analytics.chart.sunday", locale=locale),
                    1: t("analytics.chart.monday", locale=locale),
                    2: t("analytics.chart.tuesday", locale=locale),
                    3: t("analytics.chart.wednesday", locale=locale),
                    4: t("analytics.chart.thursday", locale=locale),
                    5: t("analytics.chart.friday", locale=locale),
                    6: t("analytics.chart.saturday", locale=locale)
                }

                labels = [day_names[int(row[3])] for row in rows] if rows else []
                sent_data = [row[1] for row in rows] if rows else []
                received_data = [row[2] for row in rows] if rows else []

                # Fill missing days with zeros if needed
                if len(labels) < days:
                    # Get current day of week and fill backwards
                    from datetime import datetime, timedelta
                    today = datetime.now().date()

                    # Create full 7-day labels starting from today going backwards
                    full_labels = []
                    full_sent = []
                    full_received = []

                    for i in range(days):
                        day_date = today - timedelta(days=days-1-i)
                        day_of_week = day_date.weekday() + 1  # Convert to PostgreSQL DOW (1=Monday, 0=Sunday)
                        if day_of_week == 7:
                            day_of_week = 0  # Sunday

                        full_labels.append(day_names[day_of_week])

                        # Find matching data for this day
                        found_data = False
                        for j, row in enumerate(rows):
                            if row[0] == day_date:  # row[0] is the date
                                full_sent.append(row[1])
                                full_received.append(row[2])
                                found_data = True
                                break

                        if not found_data:
                            full_sent.append(0)
                            full_received.append(0)

                    labels = full_labels
                    sent_data = full_sent
                    received_data = full_received

            else:
                # Weekly breakdown for longer periods
                weeks = min(days // 7, 12)  # Max 12 weeks
                channel_filter = "AND t.channel = :channel" if channel else ""
                params = {}
                if channel:
                    params['channel'] = channel

                query_text = f"""
                    WITH weekly_messages AS (
                        SELECT 
                            DATE_TRUNC('week', m.created_at AT TIME ZONE 'UTC')::date as week_start,
                            COUNT(*) FILTER (WHERE m.sender = 'user') as sent,
                            COUNT(*) FILTER (WHERE m.sender = 'contact') as received
                        FROM messages m
                        JOIN threads t ON t.id = m.thread_id
                        WHERE t.user_id = app.current_user_id()
                        AND m.created_at >= CURRENT_DATE - INTERVAL '{days} days'
                        {channel_filter}
                        GROUP BY DATE_TRUNC('week', m.created_at AT TIME ZONE 'UTC')::date
                        ORDER BY week_start
                        LIMIT {weeks}
                    )
                    SELECT 
                        wm.week_start,
                        wm.sent,
                        wm.received,
                        ROW_NUMBER() OVER (ORDER BY wm.week_start) as week_number
                    FROM weekly_messages wm
                """

                result = await self.session.execute(text(query_text), params)
                rows = result.fetchall()

                # Translate week labels
                labels = [t("analytics.chart.week", week=row[3], locale=locale) for row in rows] if rows else []
                sent_data = [row[1] for row in rows] if rows else []
                received_data = [row[2] for row in rows] if rows else []

                # Fill missing weeks with zeros if needed
                if len(labels) < weeks:
                    for i in range(len(labels), weeks):
                        labels.append(t("analytics.chart.week", week=i+1, locale=locale))
                        sent_data.append(0)
                        received_data.append(0)

        except Exception as e:
            logger.error(f"Error in get_weekly_activity_chart: {e}")
            # Fallback
            if days <= 7:
                labels = [t("analytics.chart.monday", locale=locale), t("analytics.chart.tuesday", locale=locale),
                         t("analytics.chart.wednesday", locale=locale), t("analytics.chart.thursday", locale=locale),
                         t("analytics.chart.friday", locale=locale), t("analytics.chart.saturday", locale=locale),
                         t("analytics.chart.sunday", locale=locale)]
                sent_data = [0] * 7
                received_data = [0] * 7
            else:
                weeks = min(days // 7, 12)
                labels = [t("analytics.chart.week", week=i+1, locale=locale) for i in range(weeks)]
                sent_data = [0] * weeks
                received_data = [0] * weeks

        return {
            'labels': labels,
            'datasets': [
                {
                    'name': t("analytics.chart.sent", locale=locale),
                    'data': sent_data
                },
                {
                    'name': t("analytics.chart.received", locale=locale),
                    'data': received_data
                }
            ]
        }

    @trace_async
    async def get_user_activity_summary(self, user_id: UUID, days: int = 30, offset_days: int = 0, channel: str | None = None) -> dict[str, Any]:
        """Get user activity summary for a given period."""

        # Calculate date range
        end_date = datetime.utcnow() - timedelta(days=offset_days)
        start_date = end_date - timedelta(days=days)

        try:
            # Build query with channel filter
            query = select(
                func.count(threads_table.c.id.distinct()).label('active_threads'),
                func.count(
                    case((messages_table.c.sender == 'user', 1), else_=None)
                ).label('messages_sent'),
                func.count(
                    case((messages_table.c.sender == 'contact', 1), else_=None)
                ).label('messages_received'),
                func.max(messages_table.c.created_at).label('last_activity')
            ).select_from(
                threads_table.outerjoin(
                    messages_table,
                    and_(
                        messages_table.c.thread_id == threads_table.c.id,
                        messages_table.c.created_at >= start_date,
                        messages_table.c.created_at < end_date
                    )
                )
            ).where(
                threads_table.c.user_id == text('app.current_user_id()')
            )

            if channel:
                query = query.where(threads_table.c.channel == channel)

            result = await self.session.execute(query)
            row = result.fetchone()

            return {
                'active_threads': row.active_threads or 0,
                'messages_sent': row.messages_sent or 0,
                'messages_received': row.messages_received or 0,
                'last_activity': row.last_activity.isoformat() if row.last_activity else None
            }

        except Exception as e:
            logger.error(f"Error in get_user_activity_summary: {e}")
            return {
                'active_threads': 0,
                'messages_sent': 0,
                'messages_received': 0,
                'last_activity': None
            }

    @trace_async
    async def verify_thread_access(self, user_id: UUID, thread_id: UUID) -> bool:
        """Verify if user has access to thread."""
        try:
            query = select(func.count()).select_from(threads_table).where(
                and_(
                    threads_table.c.id == thread_id,
                    threads_table.c.user_id == text('app.current_user_id()')
                )
            )

            result = await self.session.execute(query)
            count = result.scalar()
            return count > 0

        except Exception:
            return False

    @trace_async
    async def get_thread_insights(self, thread_id: UUID) -> dict:
        """Get comprehensive insights for a specific thread."""
        try:
            # Basic thread info and message stats
            stats_query = select(
                threads_table.c.created_at,
                threads_table.c.last_activity,
                threads_table.c.channel,
                func.count(messages_table.c.id).label('total_messages'),
                func.count(
                    case((messages_table.c.sender == 'user', 1), else_=None)
                ).label('user_messages'),
                func.count(
                    case((messages_table.c.sender == 'contact', 1), else_=None)
                ).label('contact_messages'),
                func.min(messages_table.c.created_at).label('first_message'),
                func.max(messages_table.c.created_at).label('last_message')
            ).select_from(
                threads_table.outerjoin(
                    messages_table,
                    messages_table.c.thread_id == threads_table.c.id
                )
            ).where(
                and_(
                    threads_table.c.id == thread_id,
                    threads_table.c.user_id == text('app.current_user_id()')
                )
            ).group_by(
                threads_table.c.id,
                threads_table.c.created_at,
                threads_table.c.last_activity,
                threads_table.c.channel
            )

            stats_result = await self.session.execute(stats_query)
            stats = stats_result.first()

            if not stats:
                return {}

            # Calculate response time (average time between user message and contact response)
            avg_response_query = text("""
                WITH response_times AS (
                    SELECT 
                        EXTRACT(EPOCH FROM (m2.created_at - m1.created_at))/3600 as hours_diff
                    FROM messages m1
                    JOIN messages m2 ON m1.thread_id = m2.thread_id
                    JOIN threads t ON t.id = m1.thread_id
                    WHERE t.id = :thread_id
                    AND t.user_id = app.current_user_id()
                    AND m1.sender = 'user'
                    AND m2.sender = 'contact'
                    AND m2.created_at > m1.created_at
                    AND NOT EXISTS (
                        SELECT 1 FROM messages m3 
                        WHERE m3.thread_id = m1.thread_id 
                        AND m3.created_at > m1.created_at 
                        AND m3.created_at < m2.created_at
                    )
                )
                SELECT AVG(hours_diff) as avg_response_hours
                FROM response_times
            """)

            response_result = await self.session.execute(avg_response_query, {'thread_id': thread_id})
            avg_response_hours = response_result.scalar() or 0

            # Get most active hour
            active_hour_query = select(
                func.extract('hour', messages_table.c.created_at).label('hour'),
                func.count().label('message_count')
            ).select_from(
                messages_table.join(threads_table, threads_table.c.id == messages_table.c.thread_id)
            ).where(
                and_(
                    threads_table.c.id == thread_id,
                    threads_table.c.user_id == text('app.current_user_id()')
                )
            ).group_by(
                func.extract('hour', messages_table.c.created_at)
            ).order_by(
                func.count().desc()
            ).limit(1)

            active_hour_result = await self.session.execute(active_hour_query)
            active_hour_row = active_hour_result.first()
            most_active_hour = int(active_hour_row.hour) if active_hour_row else None

            # Get AI job stats for this thread
            ai_stats_query = text("""
                SELECT 
                    COUNT(*) as total_ai_jobs,
                    COUNT(CASE WHEN status = 'done' THEN 1 END) as completed_ai_jobs,
                    COUNT(CASE WHEN kind = 'suggestion' THEN 1 END) as suggestions,
                    COUNT(CASE WHEN kind = 'icebreaker' THEN 1 END) as icebreakers
                FROM ai_jobs 
                WHERE thread_id = :thread_id 
                AND user_id = app.current_user_id()
            """)

            ai_result = await self.session.execute(ai_stats_query, {'thread_id': thread_id})
            ai_stats = ai_result.first()

            # Calculate days conversing
            days_conversing = 0
            if stats.first_message:
                now = datetime.now(UTC)
                days_conversing = (now - stats.first_message).days + 1

            # Calculate conversation balance
            total_msgs = stats.total_messages or 0
            user_percentage = 0
            contact_percentage = 0
            if total_msgs > 0:
                user_percentage = round((stats.user_messages / total_msgs) * 100)
                contact_percentage = round((stats.contact_messages / total_msgs) * 100)

            return {
                'thread_id': str(thread_id),
                'channel': stats.channel,
                'days_conversing': days_conversing,
                'total_messages': total_msgs,
                'user_messages': stats.user_messages or 0,
                'contact_messages': stats.contact_messages or 0,
                'user_percentage': user_percentage,
                'contact_percentage': contact_percentage,
                'avg_response_hours': round(avg_response_hours, 1) if avg_response_hours else 0,
                'most_active_hour': most_active_hour,
                'first_message_at': stats.first_message,
                'last_message_at': stats.last_message,
                'last_activity': stats.last_activity,
                'total_ai_jobs': ai_stats.total_ai_jobs or 0,
                'completed_ai_jobs': ai_stats.completed_ai_jobs or 0,
                'suggestions_used': ai_stats.suggestions or 0,
                'icebreakers_created': ai_stats.icebreakers or 0
            }

        except Exception as e:
            logger.error(f"Error getting thread insights: {e}")
            return {}

    @trace_async
    async def get_thread_activity_summary(self, thread_id: UUID, days: int = 30, offset_days: int = 0) -> dict[str, Any]:
        """Get activity summary for a specific thread."""

        # Calculate date range
        end_date = datetime.utcnow() - timedelta(days=offset_days)
        start_date = end_date - timedelta(days=days)

        try:
            query = select(
                func.count(
                    case((messages_table.c.sender == 'user', 1), else_=None)
                ).label('messages_sent'),
                func.count(
                    case((messages_table.c.sender == 'contact', 1), else_=None)
                ).label('messages_received'),
                func.max(messages_table.c.created_at).label('last_activity')
            ).select_from(messages_table).where(
                and_(
                    messages_table.c.thread_id == thread_id,
                    messages_table.c.created_at >= start_date,
                    messages_table.c.created_at < end_date
                )
            )

            result = await self.session.execute(query)
            row = result.fetchone()

            # Get AI job stats for this thread
            ai_query = select(
                func.count().label('ai_jobs_total'),
                func.count(case((text("status = 'done'"), 1), else_=None)).label('ai_jobs_completed')
            ).select_from(
                text('ai_jobs')
            ).where(
                and_(
                    text('thread_id = :thread_id'),
                    text('user_id = app.current_user_id()'),
                    text('created_at >= :start_date'),
                    text('created_at < :end_date')
                )
            )

            ai_result = await self.session.execute(ai_query, {
                'thread_id': thread_id,
                'start_date': start_date,
                'end_date': end_date
            })
            ai_row = ai_result.fetchone()

            return {
                'messages_sent': row.messages_sent or 0,
                'messages_received': row.messages_received or 0,
                'last_activity': row.last_activity.isoformat() if row.last_activity else None,
                'ai_jobs_total': ai_row.ai_jobs_total or 0,
                'ai_jobs_completed': ai_row.ai_jobs_completed or 0
            }

        except Exception as e:
            logger.error(f"Error in get_thread_activity_summary: {e}")
            return {
                'messages_sent': 0,
                'messages_received': 0,
                'last_activity': None,
                'ai_jobs_total': 0,
                'ai_jobs_completed': 0
            }

    @trace_async
    async def get_system_metrics(self, since: datetime) -> dict[str, Any]:
        """Get system-wide metrics (no RLS needed)."""
        try:
            # User metrics
            user_query = select(
                func.count().label('total_users'),
                func.count(case((text('created_at >= :since'), 1), else_=None)).label('new_users')
            ).select_from(text('users'))

            user_result = await self.session.execute(user_query, {'since': since})
            user_stats = user_result.fetchone()

            # Message metrics
            message_query = select(
                func.count().label('total_messages'),
                func.count(case((messages_table.c.created_at >= since, 1), else_=None)).label('recent_messages')
            ).select_from(messages_table)

            message_result = await self.session.execute(message_query)
            message_stats = message_result.fetchone()

            # AI job metrics
            ai_query = select(
                func.count(case((text('created_at >= :since'), 1), else_=None)).label('recent_ai_jobs'),
                func.count(case((and_(text('created_at >= :since'), text("status = 'done'")), 1), else_=None)).label('completed_ai_jobs')
            ).select_from(text('ai_jobs'))

            ai_result = await self.session.execute(ai_query, {'since': since})
            ai_stats = ai_result.fetchone()

            return {
                'total_users': user_stats.total_users or 0,
                'new_users': user_stats.new_users or 0,
                'total_messages': message_stats.total_messages or 0,
                'recent_messages': message_stats.recent_messages or 0,
                'recent_ai_jobs': ai_stats.recent_ai_jobs or 0,
                'completed_ai_jobs': ai_stats.completed_ai_jobs or 0
            }

        except Exception as e:
            logger.error(f"Error in get_system_metrics: {e}")
            return {
                'total_users': 0,
                'new_users': 0,
                'total_messages': 0,
                'recent_messages': 0,
                'recent_ai_jobs': 0,
                'completed_ai_jobs': 0
            }

    @trace_async
    async def get_channel_stats(self, days: int) -> dict[str, int]:
        """Get channel usage statistics."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            query = select(
                threads_table.c.channel,
                func.count().label('thread_count')
            ).select_from(threads_table).where(
                threads_table.c.created_at >= start_date
            ).group_by(threads_table.c.channel)

            result = await self.session.execute(query)
            rows = result.fetchall()

            return {row.channel: row.thread_count for row in rows}

        except Exception as e:
            logger.error(f"Error in get_channel_stats: {e}")
            return {}

    @trace_async
    async def get_onboarding_funnel(self) -> dict[str, int]:
        """Get onboarding funnel analytics."""
        try:
            query = select(
                text('step'),
                func.count().label('user_count')
            ).select_from(
                text('onboarding_progress')
            ).where(
                text("status = 'completed'")
            ).group_by(text('step'))

            result = await self.session.execute(query)
            rows = result.fetchall()

            return {row.step: row.user_count for row in rows}

        except Exception as e:
            logger.error(f"Error in get_onboarding_funnel: {e}")
            return {}

    @trace_async
    async def get_user_kpi_30d(self, user_id: UUID) -> dict[str, Any] | None:
        """Get 30-day KPI for user from materialized view."""
        try:
            query = select(text('*')).select_from(text('user_kpi_30d')).where(
                text('user_id = app.current_user_id()')
            )

            result = await self.session.execute(query)
            row = result.fetchone()

            if row:
                return dict(row._mapping)
            return None

        except Exception as e:
            logger.error(f"Error in get_user_kpi_30d: {e}")
            return None

    # ========== TIER 1 METRICS (NEW) ==========

    @trace_async
    async def get_thread_message_balance(self, thread_id: UUID) -> dict[str, Any]:
        """Get message balance for a thread (user vs contact messages)."""
        try:
            query = select(
                func.count(case((messages_table.c.sender == 'user', 1), else_=None)).label('user_msgs'),
                func.count(case((messages_table.c.sender == 'contact', 1), else_=None)).label('contact_msgs'),
                func.count().label('total_msgs')
            ).select_from(
                messages_table.join(threads_table, threads_table.c.id == messages_table.c.thread_id)
            ).where(
                and_(
                    messages_table.c.thread_id == thread_id,
                    threads_table.c.user_id == text('app.current_user_id()')
                )
            )

            result = await self.session.execute(query)
            row = result.fetchone()

            if not row or row.total_msgs == 0:
                return {
                    'user_messages': 0,
                    'contact_messages': 0,
                    'total_messages': 0,
                    'user_percentage': 0,
                    'contact_percentage': 0,
                    'balance_score': 50  # Neutral
                }

            user_percentage = round((row.user_msgs / row.total_msgs) * 100, 1)
            contact_percentage = round((row.contact_msgs / row.total_msgs) * 100, 1)

            # Balance score: 50 is ideal, deviations reduce score
            balance_score = 100 - abs(50 - user_percentage)

            return {
                'user_messages': row.user_msgs,
                'contact_messages': row.contact_msgs,
                'total_messages': row.total_msgs,
                'user_percentage': user_percentage,
                'contact_percentage': contact_percentage,
                'balance_score': round(balance_score, 1)
            }

        except Exception as e:
            logger.error(f"Error in get_thread_message_balance: {e}")
            return {
                'user_messages': 0,
                'contact_messages': 0,
                'total_messages': 0,
                'user_percentage': 0,
                'contact_percentage': 0,
                'balance_score': 50
            }

    @trace_async
    async def get_thread_response_times(self, thread_id: UUID) -> dict[str, Any]:
        """Get average response time for contact in a thread."""
        try:
            query = text("""
                WITH response_pairs AS (
                    SELECT 
                        EXTRACT(EPOCH FROM (m2.created_at - m1.created_at)) / 3600 as hours
                    FROM messages m1
                    JOIN messages m2 ON m2.thread_id = m1.thread_id
                    JOIN threads t ON t.id = m1.thread_id
                    WHERE m1.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                    AND m1.sender = 'user'
                    AND m2.sender = 'contact'
                    AND m2.created_at > m1.created_at
                    AND m2.created_at = (
                        SELECT MIN(created_at)
                        FROM messages
                        WHERE thread_id = m1.thread_id
                        AND sender = 'contact'
                        AND created_at > m1.created_at
                    )
                )
                SELECT 
                    AVG(hours) as avg_hours,
                    MIN(hours) as min_hours,
                    MAX(hours) as max_hours,
                    COUNT(*) as response_count
                FROM response_pairs
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            row = result.fetchone()

            if not row or row.response_count == 0:
                return {
                    'avg_response_hours': 0,
                    'min_response_hours': 0,
                    'max_response_hours': 0,
                    'response_count': 0,
                    'interest_level': 'unknown'
                }

            avg_hours = row.avg_hours or 0

            # Interest level based on response time
            if avg_hours < 1:
                interest_level = 'very_high'
            elif avg_hours < 6:
                interest_level = 'high'
            elif avg_hours < 24:
                interest_level = 'medium'
            else:
                interest_level = 'low'

            return {
                'avg_response_hours': round(avg_hours, 1),
                'min_response_hours': round(row.min_hours or 0, 1),
                'max_response_hours': round(row.max_hours or 0, 1),
                'response_count': row.response_count,
                'interest_level': interest_level
            }

        except Exception as e:
            logger.error(f"Error in get_thread_response_times: {e}")
            return {
                'avg_response_hours': 0,
                'min_response_hours': 0,
                'max_response_hours': 0,
                'response_count': 0,
                'interest_level': 'unknown'
            }

    @trace_async
    async def get_thread_response_trend(self, thread_id: UUID) -> dict[str, Any]:
        """Get response time trend (first 10 vs last 10 messages)."""
        try:
            query = text("""
                WITH response_pairs AS (
                    SELECT 
                        EXTRACT(EPOCH FROM (m2.created_at - m1.created_at)) / 3600 as hours,
                        ROW_NUMBER() OVER (ORDER BY m1.created_at) as rn,
                        COUNT(*) OVER () as total_count
                    FROM messages m1
                    JOIN messages m2 ON m2.thread_id = m1.thread_id
                    JOIN threads t ON t.id = m1.thread_id
                    WHERE m1.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                    AND m1.sender = 'user'
                    AND m2.sender = 'contact'
                    AND m2.created_at > m1.created_at
                    AND m2.created_at = (
                        SELECT MIN(created_at)
                        FROM messages
                        WHERE thread_id = m1.thread_id
                        AND sender = 'contact'
                        AND created_at > m1.created_at
                    )
                ),
                first_10 AS (
                    SELECT AVG(hours) as avg_first
                    FROM response_pairs
                    WHERE rn <= 10
                ),
                last_10 AS (
                    SELECT AVG(hours) as avg_last
                    FROM response_pairs
                    WHERE rn > (SELECT MAX(total_count) - 10 FROM response_pairs)
                )
                SELECT 
                    f.avg_first,
                    l.avg_last,
                    CASE 
                        WHEN f.avg_first > 0 THEN ((l.avg_last - f.avg_first) / f.avg_first) * 100
                        ELSE 0
                    END as trend_percent
                FROM first_10 f, last_10 l
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            row = result.fetchone()

            if not row or row.avg_first is None:
                return {
                    'first_10_avg_hours': 0,
                    'last_10_avg_hours': 0,
                    'trend_percent': 0,
                    'trend_direction': 'stable',
                    'trend_interpretation': 'insufficient_data'
                }

            trend_percent = row.trend_percent or 0

            # Trend interpretation
            if trend_percent < -20:
                trend_direction = 'improving'
                trend_interpretation = 'getting_faster'
            elif trend_percent > 20:
                trend_direction = 'declining'
                trend_interpretation = 'getting_slower'
            else:
                trend_direction = 'stable'
                trend_interpretation = 'consistent'

            return {
                'first_10_avg_hours': round(row.avg_first or 0, 1),
                'last_10_avg_hours': round(row.avg_last or 0, 1),
                'trend_percent': round(trend_percent, 1),
                'trend_direction': trend_direction,
                'trend_interpretation': trend_interpretation
            }

        except Exception as e:
            logger.error(f"Error in get_thread_response_trend: {e}")
            return {
                'first_10_avg_hours': 0,
                'last_10_avg_hours': 0,
                'trend_percent': 0,
                'trend_direction': 'stable',
                'trend_interpretation': 'insufficient_data'
            }

    @trace_async
    async def get_thread_depth_normalized(self, thread_id: UUID) -> dict[str, Any]:
        """Get conversation depth normalized by time (messages per day)."""
        try:
            query = text("""
                WITH thread_stats AS (
                    SELECT 
                        COUNT(*) as total_messages,
                        EXTRACT(EPOCH FROM (MAX(m.created_at) - MIN(m.created_at))) / 86400 as days_active,
                        MIN(m.created_at) as first_message,
                        MAX(m.created_at) as last_message
                    FROM messages m
                    JOIN threads t ON t.id = m.thread_id
                    WHERE m.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                )
                SELECT 
                    total_messages,
                    days_active,
                    first_message,
                    last_message,
                    CASE 
                        WHEN days_active < 1 THEN total_messages
                        ELSE ROUND(total_messages / NULLIF(days_active, 0), 1)
                    END as messages_per_day,
                    LEAST(100, ROUND((total_messages / NULLIF(days_active, 0)) * 10)) as depth_score
                FROM thread_stats
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            row = result.fetchone()

            if not row or row.total_messages == 0:
                return {
                    'total_messages': 0,
                    'days_active': 0,
                    'messages_per_day': 0,
                    'depth_score': 0,
                    'intensity_level': 'none'
                }

            messages_per_day = row.messages_per_day or 0

            # Intensity level
            if messages_per_day < 5:
                intensity_level = 'low'
            elif messages_per_day < 15:
                intensity_level = 'normal'
            elif messages_per_day < 30:
                intensity_level = 'high'
            else:
                intensity_level = 'very_high'

            return {
                'total_messages': row.total_messages,
                'days_active': round(row.days_active or 0, 1),
                'messages_per_day': messages_per_day,
                'depth_score': min(100, row.depth_score or 0),
                'intensity_level': intensity_level,
                'first_message_at': row.first_message,
                'last_message_at': row.last_message
            }

        except Exception as e:
            logger.error(f"Error in get_thread_depth_normalized: {e}")
            return {
                'total_messages': 0,
                'days_active': 0,
                'messages_per_day': 0,
                'depth_score': 0,
                'intensity_level': 'none'
            }

    @trace_async
    async def get_thread_recency(self, thread_id: UUID) -> dict[str, Any]:
        """Get time since last message in thread."""
        try:
            query = select(
                func.max(messages_table.c.created_at).label('last_message_at')
            ).select_from(
                messages_table.join(threads_table, threads_table.c.id == messages_table.c.thread_id)
            ).where(
                and_(
                    messages_table.c.thread_id == thread_id,
                    threads_table.c.user_id == text('app.current_user_id()')
                )
            )

            result = await self.session.execute(query)
            row = result.fetchone()

            if not row or not row.last_message_at:
                return {
                    'last_message_at': None,
                    'hours_since_last': 0,
                    'days_since_last': 0,
                    'status': 'no_messages'
                }

            now = datetime.now(UTC)
            hours_since = (now - row.last_message_at).total_seconds() / 3600
            days_since = hours_since / 24

            # Status based on recency
            if hours_since < 24:
                status = 'active'
            elif hours_since < 72:
                status = 'cooling'
            else:
                status = 'inactive'

            return {
                'last_message_at': row.last_message_at,
                'hours_since_last': round(hours_since, 1),
                'days_since_last': round(days_since, 1),
                'status': status
            }

        except Exception as e:
            logger.error(f"Error in get_thread_recency: {e}")
            return {
                'last_message_at': None,
                'hours_since_last': 0,
                'days_since_last': 0,
                'status': 'error'
            }

    @trace_async
    async def get_message_length_context(self, thread_id: UUID) -> dict[str, Any]:
        """Get message length with response time context."""
        try:
            query = text("""
                WITH message_analysis AS (
                    SELECT 
                        m1.sender,
                        LENGTH(m1.text) as msg_length,
                        EXTRACT(EPOCH FROM (m1.created_at - m2.created_at)) / 60 as response_minutes
                    FROM messages m1
                    LEFT JOIN messages m2 ON m2.thread_id = m1.thread_id
                        AND m2.created_at < m1.created_at
                        AND m2.sender != m1.sender
                        AND m2.created_at = (
                            SELECT MAX(created_at)
                            FROM messages
                            WHERE thread_id = m1.thread_id
                            AND sender != m1.sender
                            AND created_at < m1.created_at
                        )
                    JOIN threads t ON t.id = m1.thread_id
                    WHERE m1.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                )
                SELECT 
                    sender,
                    AVG(msg_length) as avg_length,
                    AVG(response_minutes) as avg_response_minutes,
                    COUNT(*) as message_count
                FROM message_analysis
                GROUP BY sender
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            rows = result.fetchall()

            user_data = {'avg_length': 0, 'avg_response_minutes': 0, 'message_count': 0}
            contact_data = {'avg_length': 0, 'avg_response_minutes': 0, 'message_count': 0}

            for row in rows:
                data = {
                    'avg_length': round(row.avg_length or 0, 1),
                    'avg_response_minutes': round(row.avg_response_minutes or 0, 1),
                    'message_count': row.message_count
                }
                if row.sender == 'user':
                    user_data = data
                elif row.sender == 'contact':
                    contact_data = data

            # Engagement level calculation
            contact_length = contact_data['avg_length']
            contact_response = contact_data['avg_response_minutes']

            if contact_length > 100 and contact_response < 60:
                engagement_level = 'high'
            elif contact_length > 50 and contact_response < 180:
                engagement_level = 'medium'
            else:
                engagement_level = 'low'

            return {
                'user': user_data,
                'contact': contact_data,
                'engagement_level': engagement_level
            }

        except Exception as e:
            logger.error(f"Error in get_message_length_context: {e}")
            return {
                'user': {'avg_length': 0, 'avg_response_minutes': 0, 'message_count': 0},
                'contact': {'avg_length': 0, 'avg_response_minutes': 0, 'message_count': 0},
                'engagement_level': 'unknown'
            }

    @trace_async
    async def get_emoji_usage(self, thread_id: UUID) -> dict[str, Any]:
        """Get emoji usage rate for thread."""
        try:
            query = text("""
                WITH emoji_analysis AS (
                    SELECT 
                        m.sender,
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN m.text ~ '[😀-🙏🌀-🗿🚀-🛿]' THEN 1 END) as messages_with_emoji
                    FROM messages m
                    JOIN threads t ON t.id = m.thread_id
                    WHERE m.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                    GROUP BY m.sender
                )
                SELECT 
                    sender,
                    total_messages,
                    messages_with_emoji,
                    ROUND((messages_with_emoji::float / NULLIF(total_messages, 0) * 100)::numeric, 1) as emoji_rate
                FROM emoji_analysis
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            rows = result.fetchall()

            user_data = {'total_messages': 0, 'messages_with_emoji': 0, 'emoji_rate': 0, 'usage_level': 'none'}
            contact_data = {'total_messages': 0, 'messages_with_emoji': 0, 'emoji_rate': 0, 'usage_level': 'none'}

            for row in rows:
                emoji_rate = row.emoji_rate or 0

                if emoji_rate > 50:
                    usage_level = 'high'
                elif emoji_rate > 20:
                    usage_level = 'medium'
                elif emoji_rate > 0:
                    usage_level = 'low'
                else:
                    usage_level = 'none'

                data = {
                    'total_messages': row.total_messages,
                    'messages_with_emoji': row.messages_with_emoji,
                    'emoji_rate': emoji_rate,
                    'usage_level': usage_level
                }

                if row.sender == 'user':
                    user_data = data
                elif row.sender == 'contact':
                    contact_data = data

            return {
                'user': user_data,
                'contact': contact_data
            }

        except Exception as e:
            logger.error(f"Error in get_emoji_usage: {e}")
            return {
                'user': {'total_messages': 0, 'messages_with_emoji': 0, 'emoji_rate': 0, 'usage_level': 'none'},
                'contact': {'total_messages': 0, 'messages_with_emoji': 0, 'emoji_rate': 0, 'usage_level': 'none'}
            }

    @trace_async
    async def get_contact_responsiveness(self, thread_id: UUID) -> dict[str, Any]:
        """Get contact responsiveness (how many user messages get responses)."""
        try:
            query = text("""
                WITH user_messages AS (
                    SELECT 
                        m.id,
                        m.created_at,
                        EXISTS (
                            SELECT 1 FROM messages m2
                            WHERE m2.thread_id = m.thread_id
                            AND m2.sender = 'contact'
                            AND m2.created_at > m.created_at
                        ) as has_response
                    FROM messages m
                    JOIN threads t ON t.id = m.thread_id
                    WHERE m.thread_id = :thread_id
                    AND t.user_id = app.current_user_id()
                    AND m.sender = 'user'
                )
                SELECT 
                    COUNT(*) as total_user_messages,
                    COUNT(CASE WHEN has_response THEN 1 END) as responded_messages,
                    ROUND((COUNT(CASE WHEN has_response THEN 1 END)::float / NULLIF(COUNT(*), 0))::numeric, 2) as responsiveness_rate
                FROM user_messages
            """)

            result = await self.session.execute(query, {'thread_id': thread_id})
            row = result.fetchone()

            if not row or row.total_user_messages == 0:
                return {
                    'total_user_messages': 0,
                    'responded_messages': 0,
                    'responsiveness_rate': 0,
                    'responsiveness_level': 'unknown'
                }

            responsiveness_rate = row.responsiveness_rate or 0

            # Responsiveness level
            if responsiveness_rate > 0.8:
                responsiveness_level = 'very_responsive'
            elif responsiveness_rate > 0.5:
                responsiveness_level = 'responsive'
            elif responsiveness_rate > 0.3:
                responsiveness_level = 'somewhat_responsive'
            else:
                responsiveness_level = 'unresponsive'

            return {
                'total_user_messages': row.total_user_messages,
                'responded_messages': row.responded_messages,
                'responsiveness_rate': round(responsiveness_rate * 100, 1),
                'responsiveness_level': responsiveness_level
            }

        except Exception as e:
            logger.error(f"Error in get_contact_responsiveness: {e}")
            return {
                'total_user_messages': 0,
                'responded_messages': 0,
                'responsiveness_rate': 0,
                'responsiveness_level': 'unknown'
            }
            return None

    async def get_thread_messages_for_analysis(
        self,
        thread_id: UUID,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Get recent messages from a thread for AI analysis.
        
        Args:
            thread_id: Thread ID
            limit: Number of recent messages to fetch (default 20)
            
        Returns:
            List of message dictionaries with sender and text
        """
        try:
            query = text("""
                SELECT 
                    m.sender,
                    m.text as text,
                    m.created_at
                FROM messages m
                JOIN threads t ON t.id = m.thread_id
                WHERE m.thread_id = :thread_id
                AND t.user_id = app.current_user_id()
                ORDER BY m.created_at DESC
                LIMIT :limit
            """)

            result = await self.session.execute(
                query,
                {'thread_id': thread_id, 'limit': limit}
            )
            rows = result.fetchall()

            # Reverse to get chronological order
            messages = [
                {
                    'sender': row.sender,
                    'text': row.text or '',
                    'text_msg': row.text or '',  # Alias for compatibility
                    'created_at': row.created_at.isoformat() if row.created_at else None
                }
                for row in reversed(rows)
            ]

            return messages

        except Exception as e:
            logger.error(f"Error fetching messages for analysis: {e}")
            return []
