from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.tenant import set_tenant
from app.infrastructure.email import EmailDelivery
from app.modules.jobs.email_processor import process_email_cycle
from app.modules.jobs.service import enqueue_job
from tests.integration.auth_support import APP_URL, OWNER_URL


class CapturingEmailSender:
    def __init__(self) -> None:
        self.delivery: EmailDelivery | None = None

    async def send(self, delivery: EmailDelivery) -> None:
        self.delivery = delivery


@pytest.mark.asyncio
async def test_email_job_builds_signed_invitation_link_and_completes() -> None:
    organization_id, invitation_id = uuid4(), uuid4()
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    sender = CapturingEmailSender()
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {'id': organization_id, 'name': 'Tenant Email', 'slug': f'email-{organization_id}'},
            )

        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            job_id = await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={
                    'invitation_id': str(invitation_id),
                    'recipient': 'person@example.test',
                },
                idempotency_key=f'invitation:{invitation_id}',
            )

        processed = await process_email_cycle(
            app,
            sender=sender,
            secret='a-production-secret-with-at-least-32-characters',
            public_app_url='https://app.example.test',
        )

        assert processed == 1
        assert sender.delivery is not None
        assert sender.delivery.recipient == 'person@example.test'
        assert 'https://app.example.test/activate?token=' in sender.delivery.text
        assert str(organization_id) in sender.delivery.text
        assert 'a-production-secret' not in sender.delivery.text

        async with owner.connect() as connection:
            row = (
                await connection.execute(
                    text('select status, completed_at, last_error from outbox_jobs where id = :id'),
                    {'id': job_id},
                )
            ).one()
        assert row.status == 'completed'
        assert row.completed_at is not None
        assert row.last_error is None
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()
