from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import create_app


@pytest.mark.asyncio
async def test_login_blocks_ninth_attempt_for_same_identity_and_ip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv('APP_ENV', 'test')
    monkeypatch.setenv(
        'DATABASE_URL',
        'postgresql+asyncpg://gestao_de_funcionarios_app:local_app_only_change_me@localhost:12547/gestao_de_funcionarios',
    )
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:13547/0')
    get_settings.cache_clear()
    app = create_app()
    payload = {
        'organization': f'missing-{uuid4()}',
        'email': f'user-{uuid4()}@example.com',
        'password': 'definitely-wrong',
    }
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client,
    ):
        first_eight = [
            await client.post('/api/v1/auth/login', json=payload) for _ in range(8)
        ]
        ninth = await client.post('/api/v1/auth/login', json=payload)

    assert all(response.status_code == 401 for response in first_eight)
    assert ninth.status_code == 429
    assert ninth.json() == {'detail': 'Tente novamente mais tarde.'}
    get_settings.cache_clear()
