from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.tenant import set_tenant
from app.modules.ai.gateway import AIQuotaExceeded, AIResult, execute_ai_request
from tests.integration.auth_support import APP_URL, OWNER_URL, authenticated_client


class FakeAIProvider:
    provider_name = 'fake'
    model_name = 'fake-safe-model'

    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, *, prompt: str, max_output_tokens: int) -> AIResult:
        self.calls += 1
        assert prompt == 'Resuma este contrato.'
        assert max_output_tokens == 100
        return AIResult(text='Resumo seguro.', input_tokens=12, output_tokens=7)


@pytest.mark.asyncio
async def test_ai_gateway_records_usage_without_prompt_content() -> None:
    organization_id, user_id = uuid4(), uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    provider = FakeAIProvider()
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {'id': organization_id, 'name': 'Tenant AI', 'slug': f'ai-{organization_id}'},
            )
            await connection.execute(
                text("insert into users (id, email, password_hash) values (:id, :email, 'x')"),
                {'id': user_id, 'email': f'{user_id}@example.test'},
            )
        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            result = await execute_ai_request(
                connection,
                organization_id=organization_id,
                actor_user_id=user_id,
                prompt='Resuma este contrato.',
                max_output_tokens=100,
                provider=provider,
                hash_secret='test-secret-not-for-production',
            )
        assert result.text == 'Resumo seguro.'
        assert provider.calls == 1

        async with owner.connect() as connection:
            usage = (
                await connection.execute(
                    text(
                        'select provider, model, request_hash, input_tokens, output_tokens, status '
                        'from ai_usage_events where organization_id = :organization_id'
                    ),
                    {'organization_id': organization_id},
                )
            ).one()
        assert usage.provider == 'fake'
        assert usage.model == 'fake-safe-model'
        assert len(usage.request_hash) == 64
        assert 'Resuma' not in usage.request_hash
        assert (usage.input_tokens, usage.output_tokens, usage.status) == (12, 7, 'succeeded')
    finally:
        async with owner.begin() as connection:
            await connection.execute(text('delete from users where id = :id'), {'id': user_id})
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_ai_gateway_blocks_request_beyond_monthly_limit() -> None:
    organization_id = uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    provider = FakeAIProvider()
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {
                    'id': organization_id,
                    'name': 'Tenant Limited',
                    'slug': f'limited-{organization_id}',
                },
            )
        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            await connection.execute(
                text(
                    'insert into tenant_plans (organization_id, ai_monthly_token_limit) '
                    'values (:organization_id, 5)'
                ),
                {'organization_id': organization_id},
            )
            with pytest.raises(AIQuotaExceeded):
                await execute_ai_request(
                    connection,
                    organization_id=organization_id,
                    actor_user_id=None,
                    prompt='Resuma este contrato.',
                    max_output_tokens=100,
                    provider=provider,
                    hash_secret='test-secret-not-for-production',
                )
        assert provider.calls == 0
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_ai_endpoint_fails_closed_when_provider_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/ai/generate',
            json={
                'prompt': 'informação privada que não deve voltar no erro',
                'max_output_tokens': 50,
            },
            headers={'X-CSRF-Token': csrf},
        )
    assert response.status_code == 503
    assert 'informação privada' not in response.text
