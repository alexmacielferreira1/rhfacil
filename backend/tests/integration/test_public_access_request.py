import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.security import hash_token
from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_admin_link_accepts_one_pending_request_with_generic_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = 'candidate@example.com'
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        link = await context.client.post(
            '/api/v1/access/links',
            headers={'X-CSRF-Token': csrf},
        )
        assert link.status_code == 201, link.json()
        token = link.json()['token']

        first = await context.client.post(
            f'/api/v1/access/request/{token}',
            json={'email': email, 'name': 'Pessoa', 'reason': 'Participar do time'},
        )
        duplicate = await context.client.post(
            f'/api/v1/access/request/{token}',
            json={'email': email, 'name': 'Outro nome', 'reason': 'Nova tentativa'},
        )

        assert first.status_code == 202
        assert duplicate.status_code == 202
        expected = {'message': 'Solicitação recebida para análise.'}
        assert first.json() == expected
        assert duplicate.json() == expected

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored_link = (
                    await connection.execute(
                        text(
                            'select token_hash from organization_access_links '
                            'where organization_id = :organization_id'
                        ),
                        {'organization_id': context.organization_id},
                    )
                ).one()
                requests = (
                    await connection.execute(
                        text(
                            'select email, name, reason, status from access_requests '
                            'where organization_id = :organization_id'
                        ),
                        {'organization_id': context.organization_id},
                    )
                ).all()
        finally:
            await owner.dispose()

    assert stored_link.token_hash == hash_token(token)
    assert token not in stored_link.token_hash
    assert len(requests) == 1
    assert requests[0] == (email, 'Pessoa', 'Participar do time', 'pending')


@pytest.mark.asyncio
async def test_invalid_access_link_uses_same_generic_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        response = await context.client.post(
            '/api/v1/access/request/not-a-valid-organization-token',
            json={'email': 'candidate@example.com'},
        )

    assert response.status_code == 202
    assert response.json() == {'message': 'Solicitação recebida para análise.'}


@pytest.mark.asyncio
async def test_ninth_access_request_attempt_is_rate_limited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        link = await context.client.post(
            '/api/v1/access/links',
            headers={'X-CSRF-Token': csrf},
        )
        token = link.json()['token']
        responses = [
            await context.client.post(
                f'/api/v1/access/request/{token}',
                json={'email': 'rate-limited@example.com'},
            )
            for _ in range(9)
        ]

    assert [response.status_code for response in responses[:8]] == [202] * 8
    assert responses[8].status_code == 429
