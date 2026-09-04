from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.tenant import set_tenant
from app.modules.jobs.service import claim_next_job, enqueue_job, mark_job_failed
from tests.integration.auth_support import APP_URL, OWNER_URL


@pytest.mark.asyncio
async def test_job_queue_schema_enforces_tenant_scope_and_idempotency() -> None:
    owner = create_async_engine(OWNER_URL)
    try:
        async with owner.connect() as connection:
            row = (
                await connection.execute(
                    text(
                        """
                        select c.relrowsecurity,
                               exists (
                                   select 1 from pg_constraint
                                   where conname = 'uq_outbox_jobs_tenant_idempotency'
                               ) as has_idempotency
                        from pg_class c where c.relname = 'outbox_jobs'
                        """
                    )
                )
            ).one()
        assert row == (True, True)
    finally:
        await owner.dispose()


@pytest.mark.asyncio
async def test_enqueue_job_keeps_first_payload_for_same_idempotency_key() -> None:
    organization_id = uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {'id': organization_id, 'name': 'Tenant Jobs', 'slug': f'jobs-{organization_id}'},
            )

        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            first = await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={'recipient': 'person@example.test'},
                idempotency_key='invitation:123',
            )
            duplicate = await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={'recipient': 'changed@example.test'},
                idempotency_key='invitation:123',
            )

        async with owner.connect() as connection:
            row = (
                await connection.execute(
                    text(
                        'select id, payload, status, attempts from outbox_jobs '
                        'where organization_id = :organization_id'
                    ),
                    {'organization_id': organization_id},
                )
            ).one()
        assert duplicate == first
        assert row.id == first
        assert row.payload == {'recipient': 'person@example.test'}
        assert row.status == 'pending'
        assert row.attempts == 0
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_failed_job_is_retried_later_without_immediate_reclaim() -> None:
    organization_id = uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {'id': organization_id, 'name': 'Tenant Retry', 'slug': f'retry-{organization_id}'},
            )

        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            job_id = await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={'recipient': 'person@example.test'},
                idempotency_key='invitation:retry',
            )
            claimed = await claim_next_job(connection, organization_id=organization_id)
            assert claimed is not None
            assert claimed.id == job_id
            assert claimed.attempts == 1
            await mark_job_failed(
                connection,
                organization_id=organization_id,
                job_id=job_id,
                error='SMTP temporarily unavailable',
            )
            assert await claim_next_job(connection, organization_id=organization_id) is None

        async with owner.connect() as connection:
            row = (
                await connection.execute(
                    text(
                        'select status, attempts, available_at > created_at as delayed, last_error '
                        'from outbox_jobs where id = :job_id'
                    ),
                    {'job_id': job_id},
                )
            ).one()
        assert row.status == 'pending'
        assert row.attempts == 1
        assert row.delayed is True
        assert row.last_error == 'SMTP temporarily unavailable'
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()


@pytest.mark.asyncio
async def test_worker_discovers_only_tenants_with_available_jobs() -> None:
    organization_id = uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {
                    'id': organization_id,
                    'name': 'Tenant Worker',
                    'slug': f'worker-{organization_id}',
                },
            )
        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={'invitation_id': str(uuid4()), 'recipient': 'person@example.test'},
                idempotency_key='worker-discovery',
            )
        async with app.connect() as connection:
            discovered = await connection.scalars(text('select * from pending_job_tenants()'))
            assert discovered.all() == [organization_id]
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()
