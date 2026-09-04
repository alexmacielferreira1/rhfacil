from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_admin_reads_only_own_subscription_and_feature_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = create_async_engine(OWNER_URL)
    other_organization_id = uuid4()
    try:
        async with authenticated_client(monkeypatch, role='admin') as context:
            async with owner.begin() as connection:
                await connection.execute(
                    text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                    {
                        'id': other_organization_id,
                        'name': 'Other Tenant',
                        'slug': f'other-{other_organization_id}',
                    },
                )
                await connection.execute(
                    text(
                        'insert into tenant_subscriptions '
                        '(organization_id, plan_key, status, provider) values '
                        "(:own_id, 'starter', 'active', 'local'), "
                        "(:other_id, 'enterprise-secret', 'active', 'local')"
                    ),
                    {'own_id': context.organization_id, 'other_id': other_organization_id},
                )
                await connection.execute(
                    text(
                        'insert into plan_features '
                        '(organization_id, plan_key, feature_key, enabled) '
                        "values (:own_id, 'starter', 'reports.export', true)"
                    ),
                    {'own_id': context.organization_id},
                )

            response = await context.client.get('/api/v1/billing/subscription')
            assert response.status_code == 200
            assert response.json() == {
                'plan_key': 'starter',
                'status': 'active',
                'provider': 'local',
                'trial_ends_at': None,
                'current_period_ends_at': None,
                'features': [
                    {'key': 'reports.export', 'enabled': True, 'source': 'plan'},
                ],
            }
            assert 'enterprise-secret' not in response.text

            async with owner.connect() as connection:
                audit_count = await connection.scalar(
                    text(
                        "select count(*) from audit_events "
                        "where organization_id = :organization_id "
                        "and event_type = 'billing.subscription.viewed'"
                    ),
                    {'organization_id': context.organization_id},
                )
            assert audit_count == 1
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': other_organization_id}
            )
        await owner.dispose()


@pytest.mark.asyncio
async def test_member_cannot_read_subscription_administration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='member') as context:
        response = await context.client.get('/api/v1/billing/subscription')

    assert response.status_code == 403
