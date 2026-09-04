import pytest

from tests.integration.auth_support import authenticated_client


@pytest.mark.asyncio
async def test_current_user_returns_tenant_and_generic_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        response = await context.client.get('/api/v1/auth/me')

    assert response.status_code == 200, response.json()
    assert response.json() == {
        'user_id': str(context.user_id),
        'organization_id': str(context.organization_id),
        'email': context.email,
        'role': 'admin',
    }
