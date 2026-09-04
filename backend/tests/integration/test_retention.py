from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.tenant import set_tenant
from app.modules.maintenance.retention import (
    RetentionResult,
    apply_retention,
    run_retention_cycle,
)
from tests.integration.auth_support import APP_URL, authenticated_client


@pytest.mark.asyncio
async def test_retention_deletes_only_expired_operational_records_and_audits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        engine = create_async_engine(APP_URL)
        old_request_id, recent_request_id = uuid4(), uuid4()
        try:
            async with engine.begin() as connection:
                await set_tenant(connection, context.organization_id)
                await connection.execute(
                    text(
                        """
                        insert into user_sessions
                          (organization_id, user_id, token_hash, csrf_hash, expires_at, revoked_at,
                           created_at, updated_at)
                        values
                          (:tenant, :user, :token, :csrf, now() - interval '100 days',
                           now() - interval '100 days', now() - interval '100 days',
                           now() - interval '100 days')
                        """
                    ),
                    {
                        'tenant': context.organization_id,
                        'user': context.user_id,
                        'token': f'old-{uuid4()}',
                        'csrf': f'old-{uuid4()}',
                    },
                )
                await connection.execute(
                    text(
                        """
                        insert into data_subject_requests
                          (id, organization_id, subject_user_id, request_type, status,
                           completed_at, created_at)
                        values
                          (:old_id, :tenant, :user, 'access', 'completed',
                           now() - interval '100 days', now() - interval '100 days'),
                          (:recent_id, :tenant, :user, 'access', 'completed', now(), now())
                        """
                    ),
                    {
                        'old_id': old_request_id,
                        'recent_id': recent_request_id,
                        'tenant': context.organization_id,
                        'user': context.user_id,
                    },
                )
                settings = get_settings().model_copy(
                    update={'session_retention_days': 30, 'privacy_request_retention_days': 30}
                )
                result = await apply_retention(
                    connection, organization_id=context.organization_id, settings=settings
                )
                remaining = (
                    await connection.execute(
                        text(
                            'select id from data_subject_requests '
                            'where organization_id = :tenant order by id'
                        ),
                        {'tenant': context.organization_id},
                    )
                ).scalars().all()
                audit_count = await connection.scalar(
                    text(
                        "select count(*) from audit_events where organization_id = :tenant "
                        "and event_type = 'maintenance.retention.completed'"
                    ),
                    {'tenant': context.organization_id},
                )
        finally:
            await engine.dispose()

    assert result == RetentionResult(sessions_deleted=1, privacy_requests_deleted=1)
    assert remaining == [recent_request_id]
    assert audit_count == 1


@pytest.mark.asyncio
async def test_retention_cycle_discovers_active_tenants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        engine = create_async_engine(APP_URL)
        try:
            processed = await run_retention_cycle(engine, get_settings())
            async with engine.begin() as connection:
                await set_tenant(connection, context.organization_id)
                recorded = await connection.scalar(
                    text(
                        "select count(*) from audit_events where organization_id = :tenant "
                        "and event_type = 'maintenance.retention.completed'"
                    ),
                    {'tenant': context.organization_id},
                )
        finally:
            await engine.dispose()

    assert processed >= 1
    assert recorded == 1
