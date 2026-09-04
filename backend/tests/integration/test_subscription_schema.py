import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_subscription_and_feature_tables_are_tenant_scoped() -> None:
    """Catches a missing table, missing RLS, or incomplete tenant isolation."""
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(
                text(
                    """
                    select relname, relrowsecurity, relforcerowsecurity
                    from pg_class
                    where relname in (
                        'tenant_subscriptions',
                        'plan_features',
                        'tenant_feature_overrides'
                    )
                    order by relname
                    """
                )
            )
            assert rows.all() == [
                ('plan_features', True, True),
                ('tenant_feature_overrides', True, True),
                ('tenant_subscriptions', True, True),
            ]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_subscription_status_rejects_unknown_values() -> None:
    """Catches removal of the subscription lifecycle constraint."""
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            constraint = await connection.scalar(
                text(
                    """
                    select pg_get_constraintdef(oid)
                    from pg_constraint
                    where conname = 'ck_tenant_subscriptions_status'
                    """
                )
            )
            assert constraint is not None
            for status in ('trialing', 'active', 'past_due', 'cancelled', 'suspended'):
                assert f"'{status}'" in constraint
    finally:
        await engine.dispose()
