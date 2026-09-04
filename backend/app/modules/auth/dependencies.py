from secrets import compare_digest
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.security import hash_token
from app.core.tenant import set_tenant
from app.modules.auth.schemas import CurrentUser

SESSION_COOKIE = 'saas_session'
CSRF_COOKIE = 'saas_csrf'


async def validate_csrf(request: Request) -> None:
    csrf_cookie = request.cookies.get(CSRF_COOKIE, '')
    csrf_header = request.headers.get('X-CSRF-Token', '')
    if not csrf_cookie or not csrf_header or not compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF inválido.')


async def get_current_user(request: Request) -> CurrentUser:
    session_token = request.cookies.get(SESSION_COOKIE, '')
    try:
        tenant_id = UUID(session_token.split('.', maxsplit=1)[0])
    except (ValueError, IndexError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação necessária.'
        ) from exc

    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, tenant_id)
        row = (
            await connection.execute(
                text(
                    """
                    select u.id as user_id, u.email, m.role
                    from user_sessions s
                    join users u on u.id = s.user_id
                    join memberships m on m.user_id = u.id
                      and m.organization_id = s.organization_id
                    where s.organization_id = :tenant and s.token_hash = :token_hash
                      and s.revoked_at is null and s.expires_at > now()
                      and u.active and m.active
                    """
                ),
                {'tenant': tenant_id, 'token_hash': hash_token(session_token)},
            )
        ).one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Autenticação necessária.'
        )
    return CurrentUser(
        user_id=row.user_id,
        organization_id=tenant_id,
        email=row.email,
        role=row.role,
    )
