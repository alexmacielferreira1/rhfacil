import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.security import hash_token, verify_password
from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_create_invitation_rejects_missing_csrf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        response = await context.client.post(
            '/api/v1/auth/invitations',
            json={'email': 'blocked-invite@example.com', 'role': 'member'},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_creates_invitation_without_persisting_raw_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invited_email = 'invited-user@example.com'
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/auth/invitations',
            json={'email': invited_email, 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )

        assert response.status_code == 201, response.json()
        token = response.json()['token']
        assert len(token) >= 43

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            'select id, email, role, token_hash from invitations '
                            'where organization_id = :organization_id'
                        ),
                        {'organization_id': context.organization_id},
                    )
                ).one()
                audit_event = await connection.scalar(
                    text(
                        "select event_type from audit_events "
                        "where organization_id = :organization_id "
                        "and event_type = 'auth.invitation.created'"
                    ),
                    {'organization_id': context.organization_id},
                )
                queued = (
                    await connection.execute(
                        text(
                            "select job_type, payload, idempotency_key from outbox_jobs "
                            "where organization_id = :organization_id"
                        ),
                        {'organization_id': context.organization_id},
                    )
                ).one()
        finally:
            await owner.dispose()

    assert stored.email == invited_email
    assert stored.role == 'member'
    assert stored.token_hash == hash_token(token)
    assert token not in stored.token_hash
    assert audit_event == 'auth.invitation.created'
    assert queued.job_type == 'email.invitation'
    assert queued.payload == {
        'invitation_id': str(stored.id),
        'recipient': invited_email,
    }
    assert queued.idempotency_key == f'invitation:{stored.id}'
    assert token not in str(queued.payload)


@pytest.mark.asyncio
async def test_invited_user_accepts_once_and_receives_generic_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invited_email = f'new-user-{id(monkeypatch)}@example.com'
    password = 'another correct horse battery staple'
    async with authenticated_client(monkeypatch, role='owner') as context:
        csrf = context.login.cookies['saas_csrf']
        invitation = await context.client.post(
            '/api/v1/auth/invitations',
            json={'email': invited_email, 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )
        token = invitation.json()['token']

        accepted = await context.client.post(
            '/api/v1/auth/accept-invitation',
            json={'token': token, 'password': password},
        )
        assert accepted.status_code == 201, accepted.json()

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.begin() as connection:
                row = (
                    await connection.execute(
                        text(
                            """
                            select u.id, u.password_hash, m.role, i.accepted_at
                            from users u
                            join memberships m on m.user_id = u.id
                            join invitations i on i.organization_id = m.organization_id
                              and i.email = u.email
                            where u.email = :email
                            """
                        ),
                        {'email': invited_email},
                    )
                ).one()
                assert verify_password(password, row.password_hash)
                assert row.role == 'member'
                assert row.accepted_at is not None
                accepted_audit = await connection.scalar(
                    text(
                        "select event_type from audit_events "
                        "where organization_id = :organization_id "
                        "and actor_user_id = :user_id "
                        "and event_type = 'auth.invitation.accepted'"
                    ),
                    {'organization_id': context.organization_id, 'user_id': row.id},
                )
                assert accepted_audit == 'auth.invitation.accepted'
                await connection.execute(text('delete from users where id = :id'), {'id': row.id})
        finally:
            await owner.dispose()
