from collections.abc import Awaitable
from typing import Annotated, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.security import hash_token, new_token
from app.core.tenant import set_tenant
from app.modules.access_requests.schemas import (
    AccessLinkCreated,
    AccessRequestAccepted,
    PublicAccessRequest,
)
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser

router = APIRouter(prefix='/access', tags=['access'])


@router.post('/links', response_model=AccessLinkCreated, status_code=status.HTTP_201_CREATED)
async def create_access_link(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> AccessLinkCreated:
    authorize_role(user.role, {'owner', 'admin'})
    token = new_token()
    link_id = uuid4()
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        await connection.execute(
            text(
                """
                insert into organization_access_links
                    (id, organization_id, token_hash)
                values (:id, :organization_id, :token_hash)
                """
            ),
            {
                'id': link_id,
                'organization_id': user.organization_id,
                'token_hash': hash_token(token),
            },
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='access.link.created',
            target_type='organization_access_link',
            target_id=str(link_id),
        )
    return AccessLinkCreated(token=token)


@router.post(
    '/request/{public_token}',
    response_model=AccessRequestAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_access(
    public_token: str,
    payload: PublicAccessRequest,
    request: Request,
) -> AccessRequestAccepted:
    client_ip = request.client.host if request.client else 'unknown'
    identity_hash = hash_token(f'{public_token}:{str(payload.email).lower()}:{client_ip}')
    rate_key = f'access:request:{identity_hash}'
    redis = request.app.state.redis
    attempts = await cast('Awaitable[int]', redis.incr(rate_key))
    if attempts == 1:
        await cast('Awaitable[bool]', redis.expire(rate_key, 300))
    if attempts > 8:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Muitas tentativas. Aguarde antes de tentar novamente.',
        )

    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        organization_id = await connection.scalar(
            text('select resolve_access_tenant(:token_hash)'),
            {'token_hash': hash_token(public_token)},
        )
        if organization_id is None:
            return AccessRequestAccepted()
        tenant_id = UUID(str(organization_id))
        await set_tenant(connection, tenant_id)
        request_id = await connection.scalar(
            text(
                """
                insert into access_requests (organization_id, email, name, reason)
                values (:organization_id, :email, :name, :reason)
                on conflict (organization_id, lower(email)) where status = 'pending'
                do nothing
                returning id
                """
            ),
            {
                'organization_id': tenant_id,
                'email': str(payload.email).lower(),
                'name': payload.name,
                'reason': payload.reason,
            },
        )
        if request_id is not None:
            await record_audit_event(
                connection,
                organization_id=tenant_id,
                actor_user_id=None,
                event_type='access.request.created',
                target_type='access_request',
                target_id=str(request_id),
                ip_hash=hash_token(client_ip),
            )
    return AccessRequestAccepted()
