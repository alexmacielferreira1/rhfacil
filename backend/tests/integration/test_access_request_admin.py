from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_admin_lists_and_approves_pending_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        link = await context.client.post(
            '/api/v1/access/links', headers={'X-CSRF-Token': csrf}
        )
        await context.client.post(
            f"/api/v1/access/request/{link.json()['token']}",
            json={'email': 'approved-candidate@example.com', 'name': 'Candidata'},
        )

        listing = await context.client.get('/api/v1/access/requests')
        assert listing.status_code == 200
        request_id = listing.json()[0]['id']
        approval = await context.client.patch(
            f'/api/v1/access/requests/{request_id}',
            json={'decision': 'approved', 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )

        assert approval.status_code == 200
        assert approval.json()['status'] == 'approved'
        repeated = await context.client.patch(
            f'/api/v1/access/requests/{request_id}',
            json={'decision': 'approved', 'role': 'admin'},
            headers={'X-CSRF-Token': csrf},
        )
        assert repeated.status_code == 200
        assert repeated.json()['status'] == 'approved'

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            """
                            select ar.status, i.email, i.role, j.idempotency_key
                            from access_requests ar
                            join invitations i on i.organization_id = ar.organization_id
                                and i.email = ar.email
                            join outbox_jobs j on j.organization_id = ar.organization_id
                                and j.idempotency_key = 'access-request:' || ar.id::text
                            where ar.id = :request_id
                            """
                        ),
                        {'request_id': request_id},
                    )
                ).one()
        finally:
            await owner.dispose()

    assert stored == (
        'approved',
        'approved-candidate@example.com',
        'member',
        f'access-request:{request_id}',
    )


@pytest.mark.asyncio
async def test_other_tenant_request_identifier_is_not_disclosed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.patch(
            f'/api/v1/access/requests/{uuid4()}',
            json={'decision': 'approved', 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_starts_account_with_activation_invitation_not_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/auth/pending-users',
            json={'email': 'new-member@example.com', 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )

        assert response.status_code == 201
        assert response.json()['token']

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            """
                            select i.email, i.role, j.job_type
                            from invitations i
                            join outbox_jobs j on j.organization_id = i.organization_id
                                and j.idempotency_key = 'invitation:' || i.id::text
                            where i.organization_id = :tenant and i.email = :email
                            """
                        ),
                        {
                            'tenant': context.organization_id,
                            'email': 'new-member@example.com',
                        },
                    )
                ).one()
        finally:
            await owner.dispose()

    assert stored == ('new-member@example.com', 'member', 'email.invitation')


@pytest.mark.asyncio
async def test_pending_user_rejects_temporary_password_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/auth/pending-users',
            json={
                'email': 'unsafe-password@example.com',
                'role': 'member',
                'password': 'temporary-password-must-not-be-accepted',
            },
            headers={'X-CSRF-Token': csrf},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_member_cannot_list_access_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    async with authenticated_client(monkeypatch, role='member') as context:
        response = await context.client.get('/api/v1/access/requests')

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_rejected_request_cannot_later_be_approved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        request_id = uuid4()
        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.begin() as connection:
                await connection.execute(
                    text(
                        """
                        insert into access_requests (id, organization_id, email)
                        values (:id, :tenant, :email)
                        """
                    ),
                    {
                        'id': request_id,
                        'tenant': context.organization_id,
                        'email': 'rejected@example.com',
                    },
                )
        finally:
            await owner.dispose()

        csrf = context.login.cookies['saas_csrf']
        rejection = await context.client.patch(
            f'/api/v1/access/requests/{request_id}',
            json={'decision': 'rejected', 'reason': 'Sem vaga disponível'},
            headers={'X-CSRF-Token': csrf},
        )
        later_approval = await context.client.patch(
            f'/api/v1/access/requests/{request_id}',
            json={'decision': 'approved', 'role': 'member'},
            headers={'X-CSRF-Token': csrf},
        )

        assert rejection.status_code == 200
        assert rejection.json()['status'] == 'rejected'
        assert later_approval.status_code == 200
        assert later_approval.json()['status'] == 'rejected'
