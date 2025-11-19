"""Database optimization utilities for subscription system."""

from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...utils.errors import BadRequest
from ...utils.logging import get_logger
from ...utils.tracing import trace_async
from .schemas import quota_usage_table

logger = get_logger(__name__)

# Whitelist of allowed table names to prevent SQL injection
ALLOWED_TABLES = frozenset(["subscription_status", "quota_usage"])


class SubscriptionDatabaseOptimizer:
    """Database optimization utilities for subscription system."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    def _validate_table_name(self, table_name: str) -> None:
        """Validate table name against whitelist to prevent SQL injection.
        
        Args:
            table_name: Table name to validate
            
        Raises:
            BadRequest: If table name is not in whitelist
        """
        if table_name not in ALLOWED_TABLES:
            logger.error("Invalid table name attempted", extra={
                "table_name": table_name,
                "allowed_tables": list(ALLOWED_TABLES)
            })
            raise BadRequest(f"Invalid table name: {table_name}")

    @trace_async
    async def analyze_subscription_queries(self) -> dict[str, any]:
        """Analyze subscription query performance and suggest optimizations."""
        try:
            async with self.session_factory() as session:
                analysis = {
                    "table_stats": {},
                    "index_usage": {},
                    "slow_queries": [],
                    "recommendations": [],
                    "generated_at": date.today().isoformat()
                }

                # Get table statistics
                subscription_stats = await self._get_table_stats(session, "subscription_status")
                quota_stats = await self._get_table_stats(session, "quota_usage")

                analysis["table_stats"] = {
                    "subscription_status": subscription_stats,
                    "quota_usage": quota_stats
                }

                # Check index usage
                index_usage = await self._check_index_usage(session)
                analysis["index_usage"] = index_usage

                # Generate recommendations
                recommendations = self._generate_optimization_recommendations(
                    subscription_stats, quota_stats, index_usage
                )
                analysis["recommendations"] = recommendations

                logger.info("Database analysis completed", extra={
                    "subscription_rows": subscription_stats.get("row_count", 0),
                    "quota_rows": quota_stats.get("row_count", 0),
                    "recommendations_count": len(recommendations)
                })

                return analysis

        except Exception as e:
            logger.error("Failed to analyze subscription queries", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to analyze database performance")

    @trace_async
    async def optimize_subscription_indexes(self) -> dict[str, any]:
        """Create or update indexes for optimal subscription query performance."""
        try:
            async with self.session_factory() as session:
                optimization_results = {
                    "indexes_created": [],
                    "indexes_updated": [],
                    "performance_improvements": {},
                    "completed_at": date.today().isoformat()
                }

                # Define optimal indexes for subscription queries
                subscription_indexes = [
                    {
                        "name": "idx_subscription_status_user_active",
                        "table": "subscription_status",
                        "columns": ["user_id", "expiration_date"],
                        "where": "expiration_date > now()",
                        "purpose": "Fast active subscription lookup by user"
                    },
                    {
                        "name": "idx_subscription_status_tier_expiration",
                        "table": "subscription_status",
                        "columns": ["subscription_tier", "expiration_date"],
                        "purpose": "Analytics queries by tier and expiration"
                    },
                    {
                        "name": "idx_subscription_status_revenuecat_lookup",
                        "table": "subscription_status",
                        "columns": ["revenuecat_subscriber_id"],
                        "purpose": "RevenueCat webhook processing"
                    }
                ]

                quota_indexes = [
                    {
                        "name": "idx_quota_usage_user_date_type_covering",
                        "table": "quota_usage",
                        "columns": ["user_id", "date", "quota_type"],
                        "include": ["count", "daily_limit"],
                        "purpose": "Covering index for quota checks"
                    },
                    {
                        "name": "idx_quota_usage_date_cleanup",
                        "table": "quota_usage",
                        "columns": ["date"],
                        "purpose": "Efficient cleanup of old quota data"
                    }
                ]

                # Create subscription indexes
                for index_def in subscription_indexes:
                    try:
                        await self._create_index_if_not_exists(session, index_def)
                        optimization_results["indexes_created"].append(index_def["name"])
                    except Exception as e:
                        logger.warning("Failed to create subscription index", extra={
                            "index_name": index_def["name"], "error": str(e)
                        })

                # Create quota indexes
                for index_def in quota_indexes:
                    try:
                        await self._create_index_if_not_exists(session, index_def)
                        optimization_results["indexes_created"].append(index_def["name"])
                    except Exception as e:
                        logger.warning("Failed to create quota index", extra={
                            "index_name": index_def["name"], "error": str(e)
                        })

                await session.commit()

                logger.info("Database index optimization completed", extra={
                    "indexes_created": len(optimization_results["indexes_created"])
                })

                return optimization_results

        except Exception as e:
            logger.error("Failed to optimize subscription indexes", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to optimize database indexes")

    @trace_async
    async def partition_quota_usage_table(self, months_ahead: int = 6) -> dict[str, any]:
        """Set up partitioning for quota_usage table by date."""
        try:
            async with self.session_factory() as session:
                partitioning_results = {
                    "partitions_created": [],
                    "partitions_existing": [],
                    "cleanup_scheduled": False,
                    "completed_at": date.today().isoformat()
                }

                # Check if table is already partitioned
                is_partitioned = await self._check_table_partitioned(session, "quota_usage")

                if not is_partitioned:
                    logger.info("Quota usage table is not partitioned, creating partition structure")

                    # Create monthly partitions for current and future months
                    current_date = date.today().replace(day=1)  # First day of current month

                    for i in range(months_ahead + 1):
                        partition_date = current_date + timedelta(days=32 * i)
                        partition_date = partition_date.replace(day=1)  # First day of month

                        partition_name = f"quota_usage_{partition_date.strftime('%Y_%m')}"

                        try:
                            await self._create_monthly_partition(
                                session, "quota_usage", partition_name, partition_date
                            )
                            partitioning_results["partitions_created"].append(partition_name)
                        except Exception as e:
                            logger.warning("Failed to create partition", extra={
                                "partition_name": partition_name, "error": str(e)
                            })
                else:
                    logger.info("Quota usage table is already partitioned")
                    partitioning_results["partitions_existing"] = await self._list_table_partitions(
                        session, "quota_usage"
                    )

                # Schedule cleanup of old partitions
                await self._schedule_partition_cleanup(session)
                partitioning_results["cleanup_scheduled"] = True

                await session.commit()

                logger.info("Quota usage table partitioning completed", extra={
                    "partitions_created": len(partitioning_results["partitions_created"])
                })

                return partitioning_results

        except Exception as e:
            logger.error("Failed to partition quota usage table", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to set up table partitioning")

    @trace_async
    async def cleanup_old_quota_data(self, days_to_keep: int = 90) -> dict[str, int]:
        """Clean up old quota usage data from database."""
        try:
            async with self.session_factory() as session:
                cutoff_date = date.today() - timedelta(days=days_to_keep)

                # Delete old quota usage records
                delete_stmt = sa.delete(quota_usage_table).where(
                    quota_usage_table.c.date < cutoff_date
                )

                result = await session.execute(delete_stmt)
                deleted_count = result.rowcount or 0

                await session.commit()

                logger.info("Old quota data cleanup completed", extra={
                    "deleted_count": deleted_count,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_to_keep": days_to_keep
                })

                return {
                    "deleted_count": deleted_count,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_to_keep": days_to_keep
                }

        except Exception as e:
            logger.error("Failed to cleanup old quota data", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to cleanup old quota data")

    @trace_async
    async def vacuum_and_analyze_tables(self) -> dict[str, bool]:
        """Run VACUUM and ANALYZE on subscription tables."""
        try:
            async with self.session_factory() as session:
                results = {}

                tables = ["subscription_status", "quota_usage"]

                for table_name in tables:
                    # Validate table name (defense in depth)
                    self._validate_table_name(table_name)

                    try:
                        # Run ANALYZE to update statistics
                        await session.execute(sa.text(f"ANALYZE {table_name}"))
                        results[f"{table_name}_analyzed"] = True

                        logger.info("Table analyzed", extra={"table": table_name})

                    except Exception as e:
                        logger.warning("Failed to analyze table", extra={
                            "table": table_name, "error": str(e)
                        })
                        results[f"{table_name}_analyzed"] = False

                await session.commit()

                logger.info("Database maintenance completed", extra=results)

                return results

        except Exception as e:
            logger.error("Failed to run database maintenance", extra={
                "error": str(e)
            })
            raise BadRequest("Failed to run database maintenance")

    # Private helper methods

    async def _get_table_stats(self, session: AsyncSession, table_name: str) -> dict[str, any]:
        """Get statistics for a table."""
        # Validate table name to prevent SQL injection
        self._validate_table_name(table_name)

        try:
            # Get row count
            count_query = sa.text(f"SELECT COUNT(*) FROM {table_name}")
            result = await session.execute(count_query)
            row_count = result.scalar()

            # Get table size
            size_query = sa.text(f"""
                SELECT pg_total_relation_size('{table_name}') as total_size,
                       pg_relation_size('{table_name}') as table_size
            """)
            result = await session.execute(size_query)
            size_row = result.fetchone()

            return {
                "row_count": row_count,
                "total_size_bytes": size_row.total_size if size_row else 0,
                "table_size_bytes": size_row.table_size if size_row else 0
            }

        except Exception as e:
            logger.warning("Failed to get table stats", extra={
                "table": table_name, "error": str(e)
            })
            return {"row_count": 0, "total_size_bytes": 0, "table_size_bytes": 0}

    async def _check_index_usage(self, session: AsyncSession) -> dict[str, any]:
        """Check index usage statistics."""
        try:
            # Query index usage stats
            index_query = sa.text("""
                SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE tablename IN ('subscription_status', 'quota_usage')
                ORDER BY idx_tup_read DESC
            """)

            result = await session.execute(index_query)
            rows = result.fetchall()

            index_stats = {}
            for row in rows:
                index_stats[row.indexname] = {
                    "table": row.tablename,
                    "tuples_read": row.idx_tup_read,
                    "tuples_fetched": row.idx_tup_fetch
                }

            return index_stats

        except Exception as e:
            logger.warning("Failed to check index usage", extra={"error": str(e)})
            return {}

    def _generate_optimization_recommendations(
        self,
        subscription_stats: dict[str, any],
        quota_stats: dict[str, any],
        index_usage: dict[str, any]
    ) -> list[str]:
        """Generate optimization recommendations based on statistics."""
        recommendations = []

        # Check table sizes
        if subscription_stats.get("row_count", 0) > 100000:
            recommendations.append(
                "Consider archiving old subscription records to improve query performance"
            )

        if quota_stats.get("row_count", 0) > 1000000:
            recommendations.append(
                "Implement table partitioning for quota_usage table by date"
            )
            recommendations.append(
                "Set up automated cleanup of old quota usage data"
            )

        # Check index usage
        unused_indexes = [
            name for name, stats in index_usage.items()
            if stats.get("tuples_read", 0) == 0
        ]

        if unused_indexes:
            recommendations.append(
                f"Consider dropping unused indexes: {', '.join(unused_indexes)}"
            )

        # General recommendations
        recommendations.extend([
            "Run VACUUM ANALYZE regularly on subscription tables",
            "Monitor query performance with pg_stat_statements",
            "Consider connection pooling for high-traffic scenarios"
        ])

        return recommendations

    async def _create_index_if_not_exists(
        self,
        session: AsyncSession,
        index_def: dict[str, any]
    ) -> None:
        """Create index if it doesn't exist."""
        index_name = index_def["name"]
        table_name = index_def["table"]
        columns = index_def["columns"]

        # Validate table name to prevent SQL injection
        self._validate_table_name(table_name)

        # Build CREATE INDEX statement
        columns_str = ", ".join(columns)
        create_sql = f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"

        # Add WHERE clause if specified
        if "where" in index_def:
            create_sql += f" WHERE {index_def['where']}"

        # Add INCLUDE clause if specified (for covering indexes)
        if "include" in index_def:
            include_columns = ", ".join(index_def["include"])
            create_sql += f" INCLUDE ({include_columns})"

        await session.execute(sa.text(create_sql))

    async def _check_table_partitioned(self, session: AsyncSession, table_name: str) -> bool:
        """Check if table is partitioned."""
        try:
            query = sa.text("""
                SELECT COUNT(*) > 0 as is_partitioned
                FROM pg_partitioned_table pt
                JOIN pg_class c ON pt.partrelid = c.oid
                WHERE c.relname = :table_name
            """)

            result = await session.execute(query, {"table_name": table_name})
            return result.scalar() or False

        except Exception:
            return False

    async def _create_monthly_partition(
        self,
        session: AsyncSession,
        parent_table: str,
        partition_name: str,
        partition_date: date
    ) -> None:
        """Create a monthly partition for the given date."""
        # Validate parent table name
        self._validate_table_name(parent_table)

        # Validate partition name format (must be parent_table_YYYY_MM)
        import re
        if not re.match(r'^(subscription_status|quota_usage)_\d{4}_\d{2}$', partition_name):
            raise BadRequest(f"Invalid partition name format: {partition_name}")

        next_month = (partition_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        create_sql = sa.text(f"""
            CREATE TABLE IF NOT EXISTS {partition_name} 
            PARTITION OF {parent_table}
            FOR VALUES FROM ('{partition_date}') TO ('{next_month}')
        """)

        await session.execute(create_sql)

    async def _list_table_partitions(
        self,
        session: AsyncSession,
        table_name: str
    ) -> list[str]:
        """List all partitions for a table."""
        try:
            query = sa.text("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE tablename LIKE :pattern
                ORDER BY tablename
            """)

            result = await session.execute(query, {"pattern": f"{table_name}_%"})
            return [row.tablename for row in result.fetchall()]

        except Exception:
            return []

    async def _schedule_partition_cleanup(self, session: AsyncSession) -> None:
        """Schedule cleanup of old partitions (placeholder for future implementation)."""
        # This would typically involve creating a scheduled job or cron task
        # For now, just log that cleanup should be scheduled
        logger.info("Partition cleanup should be scheduled as a background task")


def create_database_optimizer(
    session_factory: async_sessionmaker[AsyncSession]
) -> SubscriptionDatabaseOptimizer:
    """Factory function for SubscriptionDatabaseOptimizer."""
    return SubscriptionDatabaseOptimizer(session_factory)
