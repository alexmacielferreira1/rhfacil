from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_health_contract(monkeypatch) -> None:
    monkeypatch.setenv('APP_ENV', 'test')
    monkeypatch.setenv(
        'DATABASE_URL',
        'postgresql+asyncpg://user:pass@database/app',
    )
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'Gestão de Funcionários',
        'environment': 'test',
    }

    get_settings.cache_clear()
