from urllib.parse import quote
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.security import signed_token
from app.core.tenant import set_tenant
from app.infrastructure.email import EmailDelivery, EmailSender
from app.modules.jobs.service import claim_next_job, mark_job_completed, mark_job_failed


async def process_next_email_job(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    sender: EmailSender,
    secret: str,
    public_app_url: str,
) -> bool:
    job = await claim_next_job(connection, organization_id=organization_id)
    if job is None:
        return False
    try:
        if job.job_type != 'email.invitation':
            raise ValueError('Unsupported email job type.')
        invitation_id = UUID(str(job.payload['invitation_id']))
        recipient = str(job.payload['recipient'])
        subject = f'{organization_id}.{invitation_id}'
        token = signed_token(purpose='invitation', subject=subject, secret=secret)
        activation_url = f'{public_app_url.rstrip("/")}/activate?token={quote(token)}'
        await sender.send(
            EmailDelivery(
                recipient=recipient,
                subject='Convite para acessar a plataforma',
                text=f'Defina sua senha usando este link de uso único:\n\n{activation_url}',
            )
        )
    except Exception as exc:
        await mark_job_failed(
            connection,
            organization_id=organization_id,
            job_id=job.id,
            error=f'{type(exc).__name__}: {exc}',
        )
        return False
    await mark_job_completed(
        connection,
        organization_id=organization_id,
        job_id=job.id,
    )
    return True


async def process_email_cycle(
    engine: AsyncEngine,
    *,
    sender: EmailSender,
    secret: str,
    public_app_url: str,
    max_jobs: int = 100,
) -> int:
    async with engine.connect() as connection:
        tenants = list(await connection.scalars(text('select * from pending_job_tenants()')))

    completed = 0
    for tenant in tenants:
        organization_id = UUID(str(tenant))
        while completed < max_jobs:
            async with engine.begin() as connection:
                await set_tenant(connection, organization_id)
                processed = await process_next_email_job(
                    connection,
                    organization_id=organization_id,
                    sender=sender,
                    secret=secret,
                    public_app_url=public_app_url,
                )
            if not processed:
                break
            completed += 1
        if completed >= max_jobs:
            break
    return completed
