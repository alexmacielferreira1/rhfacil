from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.tenant import set_tenant
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser
from app.modules.privacy.schemas import (
    PrivacyRequestCreate,
    PrivacyRequestCreated,
    PrivacyRequestUpdate,
    PrivacyRequestUpdated,
)

router = APIRouter(prefix='/privacy', tags=['privacy'])


@router.post(
    '/requests',
    response_model=PrivacyRequestCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_privacy_request(
    payload: PrivacyRequestCreate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> PrivacyRequestCreated:
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        request_id = await connection.scalar(
            text(
                """
                insert into data_subject_requests
                    (organization_id, subject_user_id, request_type)
                values (:organization_id, :user_id, :request_type)
                returning id
                """
            ),
            {
                'organization_id': user.organization_id,
                'user_id': user.user_id,
                'request_type': payload.request_type,
            },
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='privacy.request.created',
            target_type='data_subject_request',
            target_id=str(request_id),
        )
    return PrivacyRequestCreated(id=UUID(str(request_id)))


@router.patch('/requests/{request_id}', response_model=PrivacyRequestUpdated)
async def update_privacy_request(
    request_id: UUID,
    payload: PrivacyRequestUpdate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> PrivacyRequestUpdated:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        updated_id = await connection.scalar(
            text(
                """
                update data_subject_requests
                set status = :status,
                    notes = :notes,
                    completed_at = case
                        when cast(:status as varchar) in ('completed', 'rejected') then now()
                        else null
                    end
                where id = :request_id and organization_id = :organization_id
                returning id
                """
            ),
            {
                'status': payload.status,
                'notes': payload.notes,
                'request_id': request_id,
                'organization_id': user.organization_id,
            },
        )
        if updated_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Solicitação não encontrada.',
            )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='privacy.request.updated',
            target_type='data_subject_request',
            target_id=str(request_id),
        )
    return PrivacyRequestUpdated(id=request_id, status=payload.status)
