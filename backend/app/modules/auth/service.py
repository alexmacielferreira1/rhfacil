from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import get_settings
from app.core.security import hash_token, signed_token
from app.modules.jobs.service import enqueue_job


@dataclass(frozen=True)
class IssuedInvitation:
    id: UUID
    token: str


async def issue_invitation(
    connection: AsyncConnection,
    *,
    organization_id: UUID,
    email: str,
    role: str,
    idempotency_key: str | None = None,
) -> IssuedInvitation:
    invitation_id = uuid4()
    token = signed_token(
        purpose='invitation',
        subject=f'{organization_id}.{invitation_id}',
        secret=get_settings().auth_secret,
    )
    await connection.execute(
        text(
            """
            insert into invitations
                (id, organization_id, email, role, token_hash, expires_at)
            values (:id, :tenant, :email, :role, :token_hash, :expires_at)
            """
        ),
        {
            'id': invitation_id,
            'tenant': organization_id,
            'email': email.lower(),
            'role': role,
            'token_hash': hash_token(token),
            'expires_at': datetime.now(UTC) + timedelta(hours=48),
        },
    )
    await enqueue_job(
        connection,
        organization_id=organization_id,
        job_type='email.invitation',
        payload={'invitation_id': str(invitation_id), 'recipient': email.lower()},
        idempotency_key=idempotency_key or f'invitation:{invitation_id}',
    )
    return IssuedInvitation(id=invitation_id, token=token)
