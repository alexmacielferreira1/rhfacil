import os
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_every_response_has_security_headers() -> None:
    os.environ['APP_ENV'] = 'test'
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:pass@database/app'
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get('/api/v1/health')

    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['x-frame-options'] == 'DENY'
    assert response.headers['referrer-policy'] == 'no-referrer'
    assert "default-src 'none'" in response.headers['content-security-policy']
    assert UUID(response.headers['x-request-id'])
    get_settings.cache_clear()
