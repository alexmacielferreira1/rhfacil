from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import get_settings
from app.core.tenant import set_tenant
from app.modules.ai.gateway import AIProvider, AIQuotaExceeded, AIResult, execute_ai_request
from app.modules.ai.providers import AIProviderUnavailable
from app.modules.ai.schemas import AIGenerateRequest, AIGenerateResponse
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser

router = APIRouter(prefix='/ai', tags=['ai'])


@router.post('/generate', response_model=AIGenerateResponse)
async def generate(
    payload: AIGenerateRequest,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> AIGenerateResponse:
    engine: AsyncEngine = request.app.state.db_engine
    provider: AIProvider = request.app.state.ai_provider
    result: AIResult | None = None
    error_status: int | None = None
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        try:
            result = await execute_ai_request(
                connection,
                organization_id=user.organization_id,
                actor_user_id=user.user_id,
                prompt=payload.prompt,
                max_output_tokens=payload.max_output_tokens,
                provider=provider,
                hash_secret=get_settings().auth_secret,
            )
        except AIQuotaExceeded:
            error_status = status.HTTP_429_TOO_MANY_REQUESTS
        except AIProviderUnavailable:
            error_status = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception:
            error_status = status.HTTP_502_BAD_GATEWAY
    if error_status is not None:
        raise HTTPException(status_code=error_status, detail='Serviço de IA indisponível.')
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Serviço de IA indisponível.',
        )
    return AIGenerateResponse(
        text=result.text,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
