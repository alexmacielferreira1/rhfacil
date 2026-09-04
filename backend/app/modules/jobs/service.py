import json
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


@dataclass(frozen=True)
class ClaimedJob:
    id: UUID
    job_type: str
    payload: dict[str, object]
    attempts: int


async def enqueue_job(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    job_type: str,
    payload: dict[str, object],
    idempotency_key: str,
) -> UUID:
    job_id = await connection.scalar(
        text(
            """
            insert into outbox_jobs
                (organization_id, job_type, payload, idempotency_key)
            values (:organization_id, :job_type, cast(:payload as jsonb), :idempotency_key)
            on conflict (organization_id, idempotency_key) do update
                set idempotency_key = excluded.idempotency_key
            returning id
            """
        ),
        {
            'organization_id': organization_id,
            'job_type': job_type,
            'payload': json.dumps(payload, separators=(',', ':'), sort_keys=True),
            'idempotency_key': idempotency_key,
        },
    )
    return UUID(str(job_id))


async def claim_next_job(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
) -> ClaimedJob | None:
    row = (
        await connection.execute(
            text(
                """
                update outbox_jobs
                set status = 'processing', locked_at = now(), attempts = attempts + 1
                where id = (
                    select id from outbox_jobs
                    where organization_id = :organization_id
                      and status = 'pending' and available_at <= now()
                    order by available_at, created_at
                    for update skip locked
                    limit 1
                )
                returning id, job_type, payload, attempts
                """
            ),
            {'organization_id': organization_id},
        )
    ).one_or_none()
    if row is None:
        return None
    return ClaimedJob(
        id=UUID(str(row.id)),
        job_type=str(row.job_type),
        payload=dict(row.payload),
        attempts=int(row.attempts),
    )


async def mark_job_failed(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    job_id: UUID,
    error: str,
) -> None:
    await connection.execute(
        text(
            """
            update outbox_jobs
            set status = case when attempts >= max_attempts then 'failed' else 'pending' end,
                available_at = now()
                    + power(2, least(attempts, 8)) * interval '30 seconds',
                locked_at = null,
                last_error = :error
            where id = :job_id and organization_id = :organization_id
              and status = 'processing'
            """
        ),
        {
            'job_id': job_id,
            'organization_id': organization_id,
            'error': error[:1000],
        },
    )


async def mark_job_completed(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    job_id: UUID,
) -> None:
    await connection.execute(
        text(
            """
            update outbox_jobs
            set status = 'completed', completed_at = now(), locked_at = null, last_error = null
            where id = :job_id and organization_id = :organization_id
              and status = 'processing'
            """
        ),
        {'job_id': job_id, 'organization_id': organization_id},
    )
