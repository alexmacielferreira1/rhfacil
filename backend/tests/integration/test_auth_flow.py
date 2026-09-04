from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import create_app

OWNER_URL = 'postgresql+asyncpg://gestao_de_funcionarios:local_only_change_me@localhost:12547/gestao_de_funcionarios'
APP_URL = (
    'postgresql+asyncpg://gestao_de_funcionarios_app:local_app_only_change_me@localhost:12547/gestao_de_funcionarios'
)


@pytest.mark.asyncio
async def test_login_sets_httponly_session_and_stores_only_hash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organization_id, user_id = uuid4(), uuid4()
    slug = f'tenant-{organization_id}'
    email = f'user-{user_id}@example.com'
    password = 'correct horse battery staple'
    owner = create_async_engine(OWNER_URL)
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {'id': organization_id, 'name': 'Tenant Test', 'slug': slug},
            )
            await connection.execute(
                text(
                    'insert into users (id, email, password_hash, email_verified) '
                    'values (:id, :email, :password_hash, true)'
                ),
                {'id': user_id, 'email': email, 'password_hash': hash_password(password)},
            )
            await connection.execute(
                text(
                    "insert into memberships (organization_id, user_id, role) "
                    "values (:organization_id, :user_id, 'owner')"
                ),
                {'organization_id': organization_id, 'user_id': user_id},
            )

        monkeypatch.setenv('APP_ENV', 'test')
        monkeypatch.setenv('DATABASE_URL', APP_URL)
        monkeypatch.setenv('REDIS_URL', 'redis://localhost:13547/0')
        get_settings.cache_clear()
        app = create_app()
        async with (
            app.router.lifespan_context(app),
            AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client,
        ):
            response = await client.post(
                '/api/v1/auth/login',
                json={'organization': slug, 'email': email, 'password': password},
            )

        assert response.status_code == 200, response.json()
        cookie_headers = response.headers.get_list('set-cookie')
        session_header = next(
            value for value in cookie_headers if value.startswith('saas_session=')
        )
        assert 'HttpOnly' in session_header
        session_token = response.cookies['saas_session']
        assert session_token.startswith(f'{organization_id}.')

        async with owner.connect() as connection:
            stored_hash = await connection.scalar(
                text('select token_hash from user_sessions where user_id = :user_id'),
                {'user_id': user_id},
            )
        assert stored_hash
        assert session_token not in stored_hash
    finally:
        get_settings.cache_clear()
        async with owner.begin() as connection:
            await connection.execute(text('delete from users where id = :id'), {'id': user_id})
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await owner.dispose()
