from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import create_engine
from app.core.middleware import SecurityHeadersMiddleware
from app.core.redis import create_redis
from app.modules.ai.providers import DisabledAIProvider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.db_engine = create_engine(settings)
    app.state.redis = create_redis(settings)
    app.state.ai_provider = DisabledAIProvider()

    try:
        yield
    finally:
        await app.state.redis.aclose()
        await app.state.db_engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(SecurityHeadersMiddleware)
    app.include_router(api_router, prefix='/api/v1')
    return app
