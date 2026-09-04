from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def record_audit_event(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    actor_user_id: UUID | None,
    event_type: str,
    target_type: str | None = None,
    target_id: str | None = None,
    ip_hash: str | None = None,
) -> None:
    await connection.execute(
        text(
            """
            insert into audit_events
                (organization_id, actor_user_id, event_type, target_type, target_id, ip_hash)
            values (
                :organization_id, :actor_user_id, :event_type,
                :target_type, :target_id, :ip_hash
            )
            """
        ),
        {
            'organization_id': organization_id,
            'actor_user_id': actor_user_id,
            'event_type': event_type,
            'target_type': target_type,
            'target_id': target_id,
            'ip_hash': ip_hash,
        },
    )
