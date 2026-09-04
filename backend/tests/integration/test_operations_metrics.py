import pytest

from tests.integration.auth_support import authenticated_client


@pytest.mark.asyncio
async def test_admin_sees_only_aggregate_tenant_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        response = await context.client.get('/api/v1/operations/metrics')

    assert response.status_code == 200
    assert response.json() == {
        'active_members': 1,
        'pending_access_requests': 0,
        'pending_jobs': 0,
        'quarantined_files': 0,
        'ai_tokens_this_month': 0,
    }
    assert 'email' not in response.text.lower()


@pytest.mark.asyncio
async def test_member_cannot_read_operational_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='member') as context:
        response = await context.client.get('/api/v1/operations/metrics')

    assert response.status_code == 403
