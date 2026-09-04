import asyncio
import json
import urllib.request
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.tenant import set_tenant
from app.modules.jobs.service import enqueue_job

OWNER_URL = 'postgresql+asyncpg://gestao_de_funcionarios:local_only_change_me@localhost:12547/gestao_de_funcionarios'
APP_URL = (
    'postgresql+asyncpg://gestao_de_funcionarios_app:local_app_only_change_me@localhost:12547/gestao_de_funcionarios'
)


async def wait_for_message(recipient: str) -> None:
    for _attempt in range(20):
        with urllib.request.urlopen(  # noqa: S310 - fixed local smoke endpoint
            'http://localhost:14547/api/v1/messages', timeout=5
        ) as response:
            payload = json.loads(response.read())
        if recipient in json.dumps(payload):
            return
        await asyncio.sleep(0.5)
    raise RuntimeError('Worker did not deliver the invitation to Mailpit.')


async def main() -> None:
    organization_id, invitation_id = uuid4(), uuid4()
    recipient = f'smoke-{invitation_id}@example.test'
    owner = create_async_engine(OWNER_URL)
    app = create_async_engine(APP_URL)
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text('insert into organizations (id, name, slug) values (:id, :name, :slug)'),
                {
                    'id': organization_id,
                    'name': 'Worker Smoke',
                    'slug': f'worker-smoke-{organization_id}',
                },
            )
        async with app.begin() as connection:
            await set_tenant(connection, organization_id)
            await enqueue_job(
                connection,
                organization_id=organization_id,
                job_type='email.invitation',
                payload={'invitation_id': str(invitation_id), 'recipient': recipient},
                idempotency_key=f'smoke:{invitation_id}',
            )
        await wait_for_message(recipient)
        print('Worker entregou o convite descartável no Mailpit.')
    finally:
        async with owner.begin() as connection:
            await connection.execute(
                text('delete from organizations where id = :id'), {'id': organization_id}
            )
        await app.dispose()
        await owner.dispose()


if __name__ == '__main__':
    asyncio.run(main())
