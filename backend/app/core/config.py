from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_env: Literal['development', 'test', 'production'] = 'development'
    app_name: str = 'Gestão de Funcionários'
    database_url: str
    migration_database_url: str | None = None
    redis_url: str = 'redis://localhost:13547/0'
    auth_secret: str = 'development-only-change-me'
    cookie_secure: bool | None = None
    cookie_samesite: Literal['lax', 'strict'] = 'lax'
    audit_retention_days: int = Field(default=730, gt=0)
    session_retention_days: int = Field(default=90, gt=0)
    privacy_request_retention_days: int = Field(default=1825, gt=0)
    smtp_host: str = 'localhost'
    smtp_port: int = Field(default=1025, gt=0, le=65535)
    email_sender: str = 'no-reply@example.test'
    public_app_url: str = 'http://localhost:11547'
    worker_poll_seconds: float = Field(default=2.0, gt=0)
    maintenance_interval_seconds: float = Field(default=86_400.0, gt=0)
    upload_root: Path = Path('uploads')
    upload_max_bytes: int = Field(default=10 * 1024 * 1024, gt=0)

    @model_validator(mode='after')
    def validate_security(self) -> Settings:
        if self.app_env == 'production':
            if self.auth_secret == 'development-only-change-me' or len(self.auth_secret) < 32:
                raise ValueError('auth_secret must be unique and at least 32 characters')
            if self.cookie_secure is False:
                raise ValueError('cookie_secure cannot be disabled in production')
            self.cookie_secure = True
        elif self.cookie_secure is None:
            self.cookie_secure = False
        return self


@lru_cache
def get_settings() -> Settings:
    # BaseSettings supplies required values from the environment at runtime;
    # static type checkers cannot infer that external source.
    return Settings()  # type: ignore[call-arg]
