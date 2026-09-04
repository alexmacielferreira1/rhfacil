from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.tenant import set_tenant
from app.modules.access_requests.schemas import (
    AccessRequestDecision,
    AccessRequestDecisionResult,
    AccessRequestItem,
)
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser
from app.modules.auth.service import issue_invitation

router = APIRouter(prefix='/access/requests', tags=['access administration'])


@router.get('', response_model=list[AccessRequestItem])
async def list_access_requests(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[AccessRequestItem]:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        rows = (
            await connection.execute(
                text(
                    """
                    select id, email, name, reason, status, created_at
                    from access_requests
                    where organization_id = :tenant
                    order by created_at desc
                    """
                ),
                {'tenant': user.organization_id},
            )
        ).mappings()
        return [AccessRequestItem.model_validate(row) for row in rows]


@router.patch('/{request_id}', response_model=AccessRequestDecisionResult)
async def decide_access_request(
    request_id: UUID,
    payload: AccessRequestDecision,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> AccessRequestDecisionResult:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        access_request = (
            await connection.execute(
                text(
                    """
                    select id, email, status from access_requests
                    where id = :id and organization_id = :tenant
                    for update
                    """
                ),
                {'id': request_id, 'tenant': user.organization_id},
            )
        ).one_or_none()
        if access_request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Não encontrado.')
        if access_request.status != 'pending':
            return AccessRequestDecisionResult(id=request_id, status=access_request.status)

        if payload.decision == 'approved':
            await issue_invitation(
                connection,
                organization_id=user.organization_id,
                email=str(access_request.email),
                role=payload.role,
                idempotency_key=f'access-request:{request_id}',
            )

        await connection.execute(
            text(
                """
                update access_requests
                set status = :decision, decision_by_user_id = :actor,
                    decision_reason = :reason, decided_at = now()
                where id = :id and organization_id = :tenant
                """
            ),
            {
                'decision': payload.decision,
                'actor': user.user_id,
                'reason': payload.reason,
                'id': request_id,
                'tenant': user.organization_id,
            },
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type=f'access.request.{payload.decision}',
            target_type='access_request',
            target_id=str(request_id),
        )
    return AccessRequestDecisionResult(id=request_id, status=payload.decision)
