import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_rejects_unknown_environment() -> None:
    with pytest.raises(ValidationError, match='app_env'):
        Settings(
            app_env='invalid',
            database_url='postgresql+asyncpg://user:pass@database/app',
        )


def test_retention_windows_are_configurable_and_positive() -> None:
    settings = Settings(
        database_url='postgresql+asyncpg://user:pass@database/app',
        audit_retention_days=365,
        session_retention_days=30,
        privacy_request_retention_days=730,
    )
    assert settings.audit_retention_days == 365
    assert settings.session_retention_days == 30
    assert settings.privacy_request_retention_days == 730

    with pytest.raises(ValidationError, match='audit_retention_days'):
        Settings(
            database_url='postgresql+asyncpg://user:pass@database/app',
            audit_retention_days=0,
        )
