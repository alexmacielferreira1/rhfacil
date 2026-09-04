import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_auth_secret() -> None:
    with pytest.raises(ValidationError, match='auth_secret'):
        Settings(
            app_env='production',
            database_url='postgresql+asyncpg://user:pass@database/app',
            auth_secret='development-only-change-me',
        )


def test_production_accepts_long_unique_auth_secret() -> None:
    settings = Settings(
        app_env='production',
        database_url='postgresql+asyncpg://user:pass@database/app',
        auth_secret='a-production-secret-with-at-least-32-characters',
    )
    assert settings.cookie_secure is True
