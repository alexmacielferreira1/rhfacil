from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.tenant import set_tenant
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import CurrentUser
from app.modules.operations.schemas import OperationalMetrics

router = APIRouter(prefix='/operations', tags=['operations'])


@router.get('/metrics', response_model=OperationalMetrics)
async def get_operational_metrics(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> OperationalMetrics:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        row = (
            await connection.execute(
                text(
                    """
                    select
                      (select count(*) from memberships where organization_id = :tenant and active)
                        as active_members,
                      (select count(*) from access_requests where organization_id = :tenant
                        and status = 'pending') as pending_access_requests,
                      (select count(*) from outbox_jobs where organization_id = :tenant
                        and status = 'pending') as pending_jobs,
                      (select count(*) from stored_files where organization_id = :tenant
                        and status = 'quarantined') as quarantined_files,
                      (select coalesce(sum(input_tokens + output_tokens), 0)
                        from ai_usage_events where organization_id = :tenant
                        and created_at >= date_trunc('month', now())) as ai_tokens_this_month
                    """
                ),
                {'tenant': user.organization_id},
            )
        ).mappings().one()
    return OperationalMetrics.model_validate(row)
