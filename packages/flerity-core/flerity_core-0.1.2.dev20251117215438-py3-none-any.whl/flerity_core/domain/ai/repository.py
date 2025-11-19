"""AI jobs repository using existing ai_jobs table."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from flerity_core.utils.clock import utcnow

from .schemas import AIJob

# Valid job kinds for validation
VALID_KINDS = ["suggestion", "icebreaker"]


class AIJobsRepository:
    """Repository for AI jobs using existing ai_jobs table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, job: AIJob) -> AIJob:
        """Save or update AI job."""
        if job.id:
            # Update existing - use raw SQL for simplicity
            stmt = text("""
                UPDATE ai_jobs 
                SET status = :status, result = :result, error = :error, 
                    updated_at = :updated_at, priority = :priority
                WHERE id = :id
                RETURNING *
            """)
            result = await self.session.execute(stmt, {
                'id': job.id,
                'status': job.status,
                'result': json.dumps(job.result) if job.result else None,
                'error': json.dumps(job.error) if job.error else None,
                'updated_at': job.updated_at or utcnow(),
                'priority': job.priority
            })
            row = result.fetchone()
        else:
            # Insert new
            stmt = text("""
                INSERT INTO ai_jobs (user_id, thread_id, kind, params, status, 
                                   result, error, idem_key, priority, created_at, updated_at)
                VALUES (:user_id, :thread_id, :kind, :params, :status, 
                        :result, :error, :idem_key, :priority, :created_at, :updated_at)
                RETURNING *
            """)
            result = await self.session.execute(stmt, {
                'user_id': job.user_id,
                'thread_id': job.thread_id,
                'kind': job.kind,
                'params': json.dumps(job.params),
                'status': job.status,
                'result': json.dumps(job.result) if job.result else None,
                'error': json.dumps(job.error) if job.error else None,
                'idem_key': job.idem_key,
                'priority': job.priority,
                'created_at': job.created_at or utcnow(),
                'updated_at': job.updated_at or utcnow()
            })
            row = result.fetchone()

        if row:
            return self._row_to_job(row)
        raise Exception("Failed to save job")

    async def get_by_id(self, job_id: UUID) -> AIJob | None:
        """Get job by ID (respects RLS)."""
        stmt = text("SELECT * FROM ai_jobs WHERE id = :job_id")
        result = await self.session.execute(stmt, {'job_id': job_id})
        row = result.fetchone()

        if row:
            return self._row_to_job(row)
        return None

    async def get_by_idem_key(self, idem_key: str) -> AIJob | None:
        """Get job by idempotency key."""
        stmt = text("SELECT * FROM ai_jobs WHERE idem_key = :idem_key")
        result = await self.session.execute(stmt, {'idem_key': idem_key})
        row = result.fetchone()

        if row:
            return self._row_to_job(row)
        return None

    async def update_job_status(self, job_id: UUID, status: str) -> None:
        """Update job status."""
        stmt = text("""
            UPDATE ai_jobs 
            SET status = :status, updated_at = :updated_at 
            WHERE id = :job_id
        """)
        await self.session.execute(stmt, {
            'job_id': job_id,
            'status': status,
            'updated_at': utcnow()
        })

    async def complete_job(self, job_id: UUID, result: dict[str, Any], duration_ms: int) -> None:
        """Mark job as completed with result."""
        stmt = text("""
            UPDATE ai_jobs 
            SET status = 'done', result = :result, updated_at = :updated_at 
            WHERE id = :job_id
        """)
        await self.session.execute(stmt, {
            'job_id': job_id,
            'result': json.dumps(result),
            'updated_at': utcnow()
        })

    async def fail_job(self, job_id: UUID, error_data: dict[str, Any]) -> None:
        """Mark job as failed."""
        stmt = text("""
            UPDATE ai_jobs 
            SET status = 'error', error = :error, updated_at = :updated_at 
            WHERE id = :job_id
        """)
        await self.session.execute(stmt, {
            'job_id': job_id,
            'error': json.dumps(error_data),
            'updated_at': utcnow()
        })

    async def schedule_retry(self, job_id: UUID, error_data: dict[str, Any], next_retry: datetime) -> None:
        """Schedule job for retry."""
        stmt = text("""
            UPDATE ai_jobs 
            SET status = 'queued', error = :error, updated_at = :updated_at 
            WHERE id = :job_id
        """)
        await self.session.execute(stmt, {
            'job_id': job_id,
            'error': json.dumps(error_data),
            'updated_at': utcnow()
        })

    def _row_to_job(self, row: Any) -> AIJob:
        """Convert database row to AIJob."""
        return AIJob(
            id=row.id,
            user_id=row.user_id,
            thread_id=row.thread_id,
            kind=row.kind,
            params=json.loads(row.params) if row.params else {},
            status=row.status,
            result=json.loads(row.result) if row.result else None,
            error=json.loads(row.error) if row.error else None,
            idem_key=row.idem_key,
            priority=row.priority,
            created_at=row.created_at,
            updated_at=row.updated_at,
            expires_at=getattr(row, 'expires_at', None)
        )


class AIGenerationRepository:
    """Repository for AI generation audit records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, generation_id: UUID) -> dict[str, Any] | None:
        """Get generation record by ID."""
        stmt = text("""
            SELECT id, thread_id, kind, prompt_hash, params, output, generated_at
            FROM ai_generations
            WHERE id = :generation_id
        """)
        result = await self.session.execute(stmt, {'generation_id': generation_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'thread_id': row[1],
            'kind': row[2],
            'prompt_hash': row[3],
            'params': row[4],  # Already a dict (JSONB)
            'output': row[5],  # Already a dict (JSONB)
            'generated_at': row[6]
        }

    async def create_generation_record(
        self,
        thread_id: UUID | None,
        kind: str,
        prompt_hash: str,
        params: dict[str, Any],
        output: dict[str, Any]
    ) -> UUID:
        """Create audit record for AI generation. Returns generation_id."""
        stmt = text("""
            INSERT INTO ai_generations (thread_id, kind, prompt_hash, params, output, generated_at)
            VALUES (:thread_id, :kind, :prompt_hash, :params, :output, :generated_at)
            RETURNING id
        """)
        result = await self.session.execute(stmt, {
            'thread_id': thread_id,
            'kind': kind,
            'prompt_hash': prompt_hash,
            'params': json.dumps(params),
            'output': json.dumps(output),
            'generated_at': utcnow()
        })
        row = result.fetchone()
        return row[0]  # Return the generated UUID
