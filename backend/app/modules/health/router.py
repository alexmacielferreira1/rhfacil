from collections.abc import Awaitable
from typing import Literal, cast

from fastapi import APIRouter, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import get_settings
from app.modules.health.schemas import (
    HealthResponse,
    ServicesHealthResponse,
    ServiceStatuses,
)

router = APIRouter(prefix='/health', tags=['health'])


@router.get('', response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service=settings.app_name,
        environment=settings.app_env,
    )


@router.get('/services', response_model=ServicesHealthResponse)
async def services_health(request: Request, response: Response) -> ServicesHealthResponse:
    database_status: Literal['ok', 'error'] = 'error'
    redis_status: Literal['ok', 'error'] = 'error'

    engine: AsyncEngine = request.app.state.db_engine
    redis_client: Redis = request.app.state.redis

    try:
        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))
        database_status = 'ok'
    except Exception:  # The public response must not expose connection details.
        pass

    try:
        if await cast('Awaitable[bool]', redis_client.ping()):
            redis_status = 'ok'
    except Exception:  # The public response must not expose connection details.
        pass

    overall_status: Literal['ok', 'error'] = (
        'ok' if database_status == redis_status == 'ok' else 'error'
    )
    if overall_status == 'error':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ServicesHealthResponse(
        status=overall_status,
        services=ServiceStatuses(
            database=database_status,
            redis=redis_status,
        ),
    )
