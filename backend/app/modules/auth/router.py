from collections.abc import Awaitable
from datetime import UTC, datetime, timedelta
from secrets import compare_digest
from typing import Annotated, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.config import get_settings
from app.core.security import hash_password, hash_token, new_token, verify_password
from app.core.tenant import set_tenant
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import (
    AuthResponse,
    CurrentUser,
    InvitationAccept,
    InvitationCreate,
    InvitationCreated,
    LoginRequest,
    PendingUserCreate,
)
from app.modules.auth.service import issue_invitation

router = APIRouter(prefix='/auth', tags=['authentication'])
SESSION_COOKIE = 'saas_session'
CSRF_COOKIE = 'saas_csrf'


async def enforce_login_limit(request: Request, payload: LoginRequest) -> str:
    client_ip = request.client.host if request.client else 'unknown'
    identity = f'{payload.organization.lower()}:{str(payload.email).lower()}:{client_ip}'
    key = f'auth:login:{hash_token(identity)}'
    redis = request.app.state.redis
    attempts = await cast('Awaitable[int]', redis.incr(key))
    if attempts == 1:
        await cast('Awaitable[bool]', redis.expire(key, 300))
    if attempts > 8:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Tente novamente mais tarde.',
        )
    return key


@router.get('/me', response_model=CurrentUser)
async def current_user(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    return user


@router.post(
    '/invitations',
    response_model=InvitationCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    payload: InvitationCreate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> InvitationCreated:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        invitation = await issue_invitation(
            connection,
            organization_id=user.organization_id,
            email=str(payload.email),
            role=payload.role,
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='auth.invitation.created',
            target_type='invitation',
            target_id=str(invitation.id),
        )
    return InvitationCreated(token=invitation.token)


@router.post(
    '/pending-users',
    response_model=InvitationCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_pending_user(
    payload: PendingUserCreate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> InvitationCreated:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        invitation = await issue_invitation(
            connection,
            organization_id=user.organization_id,
            email=str(payload.email),
            role=payload.role,
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='auth.pending_user.created',
            target_type='invitation',
            target_id=str(invitation.id),
        )
    return InvitationCreated(token=invitation.token)


@router.post(
    '/accept-invitation',
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_invitation(payload: InvitationAccept, request: Request) -> AuthResponse:
    try:
        tenant_id = UUID(payload.token.split('.', maxsplit=1)[0])
    except (ValueError, IndexError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Convite inválido ou expirado.'
        ) from exc

    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, tenant_id)
        invitation = (
            await connection.execute(
                text(
                    """
                    select id, email, role from invitations
                    where organization_id = :tenant and token_hash = :token_hash
                      and accepted_at is null and expires_at > now()
                    for update
                    """
                ),
                {'tenant': tenant_id, 'token_hash': hash_token(payload.token)},
            )
        ).one_or_none()
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Convite inválido ou expirado.',
            )
        existing_user = await connection.scalar(
            text('select id from users where lower(email) = lower(:email)'),
            {'email': invitation.email},
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Este e-mail já possui uma conta.',
            )

        user_id = uuid4()
        await connection.execute(
            text(
                """
                insert into users (id, email, password_hash, email_verified)
                values (:id, :email, :password_hash, true)
                """
            ),
            {
                'id': user_id,
                'email': invitation.email,
                'password_hash': hash_password(payload.password),
            },
        )
        await connection.execute(
            text(
                """
                insert into memberships (organization_id, user_id, role)
                values (:tenant, :user_id, :role)
                """
            ),
            {'tenant': tenant_id, 'user_id': user_id, 'role': invitation.role},
        )
        await connection.execute(
            text('update invitations set accepted_at = now() where id = :id'),
            {'id': invitation.id},
        )
        await record_audit_event(
            connection,
            organization_id=tenant_id,
            actor_user_id=user_id,
            event_type='auth.invitation.accepted',
            target_type='invitation',
            target_id=str(invitation.id),
        )
    return AuthResponse()


@router.post('/login', response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request, response: Response) -> AuthResponse:
    limit_key = await enforce_login_limit(request, payload)
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        organization_id = await connection.scalar(
            text('select id from organizations where slug = :slug and active'),
            {'slug': payload.organization.lower()},
        )
        if organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais inválidas.'
            )

        tenant_id = UUID(str(organization_id))
        await set_tenant(connection, tenant_id)
        user = (
            await connection.execute(
                text(
                    """
                    select u.id, u.password_hash
                    from users u join memberships m on m.user_id = u.id
                    where m.organization_id = :tenant and lower(u.email) = lower(:email)
                      and u.active and m.active
                    """
                ),
                {'tenant': tenant_id, 'email': str(payload.email)},
            )
        ).one_or_none()
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais inválidas.'
            )

        session_token = f'{tenant_id}.{new_token()}'
        csrf_token = new_token()
        await connection.execute(
            text(
                """
                insert into user_sessions
                    (organization_id, user_id, token_hash, csrf_hash, expires_at)
                values (:tenant, :user, :token_hash, :csrf_hash, :expires_at)
                """
            ),
            {
                'tenant': tenant_id,
                'user': user.id,
                'token_hash': hash_token(session_token),
                'csrf_hash': hash_token(csrf_token),
                'expires_at': datetime.now(UTC) + timedelta(hours=12),
            },
        )
        client_ip = request.client.host if request.client else 'unknown'
        await record_audit_event(
            connection,
            organization_id=tenant_id,
            actor_user_id=user.id,
            event_type='auth.login.succeeded',
            target_type='user',
            target_id=str(user.id),
            ip_hash=hash_token(client_ip),
        )

    await cast('Awaitable[int]', request.app.state.redis.delete(limit_key))
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        httponly=True,
        secure=bool(settings.cookie_secure),
        samesite=settings.cookie_samesite,
        max_age=43_200,
        path='/',
    )
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        httponly=False,
        secure=bool(settings.cookie_secure),
        samesite=settings.cookie_samesite,
        max_age=43_200,
        path='/',
    )
    return AuthResponse()


@router.post('/logout', response_model=AuthResponse)
async def logout(request: Request, response: Response) -> AuthResponse:
    session_token = request.cookies.get(SESSION_COOKIE, '')
    csrf_cookie = request.cookies.get(CSRF_COOKIE, '')
    csrf_header = request.headers.get('X-CSRF-Token', '')
    if not all((session_token, csrf_cookie, csrf_header)) or not compare_digest(
        csrf_cookie, csrf_header
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF inválido.')

    try:
        tenant_id = UUID(session_token.split('.', maxsplit=1)[0])
    except (ValueError, IndexError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Sessão inválida.'
        ) from exc

    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, tenant_id)
        revoked_user_id = await connection.scalar(
            text(
                """
                update user_sessions set revoked_at = now()
                where organization_id = :tenant and token_hash = :token_hash
                  and csrf_hash = :csrf_hash and revoked_at is null
                returning user_id
                """
            ),
            {
                'tenant': tenant_id,
                'token_hash': hash_token(session_token),
                'csrf_hash': hash_token(csrf_header),
            },
        )
        if revoked_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Sessão inválida.'
            )
        await record_audit_event(
            connection,
            organization_id=tenant_id,
            actor_user_id=UUID(str(revoked_user_id)),
            event_type='auth.logout.succeeded',
            target_type='session',
        )

    response.delete_cookie(SESSION_COOKIE, path='/')
    response.delete_cookie(CSRF_COOKIE, path='/')
    return AuthResponse()
