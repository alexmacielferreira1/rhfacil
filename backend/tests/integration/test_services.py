import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import create_app


@pytest.mark.asyncio
async def test_health_reports_database_and_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('APP_ENV', 'test')
    monkeypatch.setenv('DATABASE_URL', os.environ['DATABASE_URL'])
    monkeypatch.setenv('REDIS_URL', os.environ['REDIS_URL'])
    get_settings.cache_clear()

    app = create_app()
    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',
        ) as client,
    ):
        response = await client.get('/api/v1/health/services')

    assert response.status_code == 200, response.json()
    assert response.json()['services'] == {
        'database': 'ok',
        'redis': 'ok',
    }

    get_settings.cache_clear()
