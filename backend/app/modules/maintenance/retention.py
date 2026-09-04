from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.config import Settings
from app.modules.audit.service import record_audit_event


@dataclass(frozen=True)
class RetentionResult:
    sessions_deleted: int
    privacy_requests_deleted: int


async def run_retention_cycle(engine: AsyncEngine, settings: Settings) -> int:
    async with engine.connect() as connection:
        organization_ids = (
            await connection.execute(text('select id from organizations where active'))
        ).scalars().all()
    for organization_id in organization_ids:
        tenant_id = UUID(str(organization_id))
        async with engine.begin() as connection:
            await connection.execute(
                text("select set_config('app.current_tenant_id', :tenant, true)"),
                {'tenant': str(tenant_id)},
            )
            await apply_retention(
                connection,
                organization_id=tenant_id,
                settings=settings,
            )
    return len(organization_ids)


async def apply_retention(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    settings: Settings,
) -> RetentionResult:
    sessions = await connection.execute(
        text(
            """
            delete from user_sessions
            where organization_id = :tenant
              and (revoked_at is not null or expires_at < now())
              and created_at < now() - make_interval(days => :retention_days)
            """
        ),
        {
            'tenant': organization_id,
            'retention_days': settings.session_retention_days,
        },
    )
    privacy_requests = await connection.execute(
        text(
            """
            delete from data_subject_requests
            where organization_id = :tenant
              and status in ('completed', 'rejected')
              and coalesce(completed_at, created_at)
                < now() - make_interval(days => :retention_days)
            """
        ),
        {
            'tenant': organization_id,
            'retention_days': settings.privacy_request_retention_days,
        },
    )
    await record_audit_event(
        connection,
        organization_id=organization_id,
        actor_user_id=None,
        event_type='maintenance.retention.completed',
        target_type='organization',
        target_id=str(organization_id),
    )
    return RetentionResult(
        sessions_deleted=sessions.rowcount,
        privacy_requests_deleted=privacy_requests.rowcount,
    )
