import hashlib
import hmac
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


@dataclass(frozen=True)
class AIResult:
    text: str
    input_tokens: int
    output_tokens: int


class AIProvider(Protocol):
    provider_name: str
    model_name: str

    async def generate(self, *, prompt: str, max_output_tokens: int) -> AIResult: ...


class AIQuotaExceeded(Exception):
    """Raised before provider access when the tenant quota is exhausted."""


def keyed_request_hash(value: str, secret: str) -> str:
    return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()


async def execute_ai_request(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    actor_user_id: UUID | None,
    prompt: str,
    max_output_tokens: int,
    provider: AIProvider,
    hash_secret: str,
) -> AIResult:
    await connection.execute(
        text(
            """
            insert into tenant_plans (organization_id)
            values (:organization_id)
            on conflict (organization_id) do nothing
            """
        ),
        {'organization_id': organization_id},
    )
    monthly_limit = await connection.scalar(
        text(
            'select ai_monthly_token_limit from tenant_plans '
            'where organization_id = :organization_id and active'
        ),
        {'organization_id': organization_id},
    )
    used_tokens = await connection.scalar(
        text(
            """
            select coalesce(sum(input_tokens + output_tokens), 0)
            from ai_usage_events
            where organization_id = :organization_id
              and status = 'succeeded'
              and created_at >= date_trunc('month', now())
            """
        ),
        {'organization_id': organization_id},
    )
    estimated_input_tokens = max(1, (len(prompt) + 3) // 4)
    requested_tokens = estimated_input_tokens + max_output_tokens
    request_hash = keyed_request_hash(prompt, hash_secret)
    if monthly_limit is None or int(used_tokens or 0) + requested_tokens > int(monthly_limit):
        await _record_usage(
            connection,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            provider=provider,
            request_hash=request_hash,
            input_tokens=estimated_input_tokens,
            output_tokens=0,
            status='blocked',
            error_code='monthly_quota_exceeded',
        )
        raise AIQuotaExceeded

    try:
        result = await provider.generate(prompt=prompt, max_output_tokens=max_output_tokens)
    except Exception as exc:
        await _record_usage(
            connection,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            provider=provider,
            request_hash=request_hash,
            input_tokens=estimated_input_tokens,
            output_tokens=0,
            status='failed',
            error_code=type(exc).__name__[:80],
        )
        raise
    await _record_usage(
        connection,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        provider=provider,
        request_hash=request_hash,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        status='succeeded',
        error_code=None,
    )
    return result


async def _record_usage(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    actor_user_id: UUID | None,
    provider: AIProvider,
    request_hash: str,
    input_tokens: int,
    output_tokens: int,
    status: str,
    error_code: str | None,
) -> None:
    await connection.execute(
        text(
            """
            insert into ai_usage_events
                (organization_id, actor_user_id, provider, model, request_hash,
                 input_tokens, output_tokens, status, error_code)
            values (:organization_id, :actor_user_id, :provider, :model, :request_hash,
                    :input_tokens, :output_tokens, :status, :error_code)
            """
        ),
        {
            'organization_id': organization_id,
            'actor_user_id': actor_user_id,
            'provider': provider.provider_name,
            'model': provider.model_name,
            'request_hash': request_hash,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'status': status,
            'error_code': error_code,
        },
    )
