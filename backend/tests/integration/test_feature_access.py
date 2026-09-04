from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.core.tenant import set_tenant
from app.modules.billing.service import has_feature
from tests.integration.auth_support import APP_URL, OWNER_URL


async def create_organization(connection: AsyncConnection, name: str) -> UUID:
    organization_id = uuid4()
    await connection.execute(
        text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
        {'id': organization_id, 'name': name, 'slug': f'feature-{organization_id}'},
    )
    return organization_id


async def configure_subscription(
    connection: AsyncConnection,
    organization_id: UUID,
    *,
    status: str,
    trial_ends_at: datetime | None = None,
) -> None:
    await set_tenant(connection, organization_id)
    await connection.execute(
        text(
            'insert into tenant_subscriptions '
            '(organization_id, plan_key, status, trial_ends_at) '
            'values (:organization_id, :plan_key, :status, :trial_ends_at)'
        ),
        {
            'organization_id': organization_id,
            'plan_key': 'starter',
            'status': status,
            'trial_ends_at': trial_ends_at,
        },
    )
    await connection.execute(
        text(
            'insert into plan_features (organization_id, plan_key, feature_key, enabled) '
            "values (:organization_id, 'starter', 'reports.export', true)"
        ),
        {'organization_id': organization_id},
    )


@pytest.mark.asyncio
async def test_active_trial_allows_a_plan_feature() -> None:
    owner, app = create_async_engine(OWNER_URL), create_async_engine(APP_URL)
    organization_id: UUID | None = None
    try:
        async with owner.begin() as connection:
            organization_id = await create_organization(connection, 'Active Trial')
        async with app.begin() as connection:
            await configure_subscription(
                connection,
                organization_id,
                status='trialing',
                trial_ends_at=datetime.now(UTC) + timedelta(days=7),
            )
            assert await has_feature(connection, organization_id, 'reports.export') is True
    finally:
        if organization_id is not None:
            async with owner.begin() as connection:
                await connection.execute(
                    text('delete from organizations where id = :id'), {'id': organization_id}
                )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_suspended_subscription_blocks_an_enabled_feature() -> None:
    owner, app = create_async_engine(OWNER_URL), create_async_engine(APP_URL)
    organization_id: UUID | None = None
    try:
        async with owner.begin() as connection:
            organization_id = await create_organization(connection, 'Suspended')
        async with app.begin() as connection:
            await configure_subscription(connection, organization_id, status='suspended')
            assert await has_feature(connection, organization_id, 'reports.export') is False
    finally:
        if organization_id is not None:
            async with owner.begin() as connection:
                await connection.execute(
                    text('delete from organizations where id = :id'), {'id': organization_id}
                )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_unknown_feature_fails_closed() -> None:
    owner, app = create_async_engine(OWNER_URL), create_async_engine(APP_URL)
    organization_id: UUID | None = None
    try:
        async with owner.begin() as connection:
            organization_id = await create_organization(connection, 'Unknown Feature')
        async with app.begin() as connection:
            await configure_subscription(connection, organization_id, status='active')
            assert await has_feature(connection, organization_id, 'unknown.feature') is False
    finally:
        if organization_id is not None:
            async with owner.begin() as connection:
                await connection.execute(
                    text('delete from organizations where id = :id'), {'id': organization_id}
                )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_tenant_override_takes_priority_over_plan_feature() -> None:
    owner, app = create_async_engine(OWNER_URL), create_async_engine(APP_URL)
    organization_id: UUID | None = None
    try:
        async with owner.begin() as connection:
            organization_id = await create_organization(connection, 'Override')
        async with app.begin() as connection:
            await configure_subscription(connection, organization_id, status='active')
            await connection.execute(
                text(
                    'insert into tenant_feature_overrides '
                    '(organization_id, feature_key, enabled) '
                    "values (:organization_id, 'reports.export', false)"
                ),
                {'organization_id': organization_id},
            )
            assert await has_feature(connection, organization_id, 'reports.export') is False
    finally:
        if organization_id is not None:
            async with owner.begin() as connection:
                await connection.execute(
                    text('delete from organizations where id = :id'), {'id': organization_id}
                )
        await app.dispose()
        await owner.dispose()
