from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def set_tenant(connection: AsyncConnection, tenant_id: UUID) -> None:
    await connection.execute(
        text("select set_config('app.current_tenant_id', :tenant_id, true)"),
        {'tenant_id': str(tenant_id)},
    )
