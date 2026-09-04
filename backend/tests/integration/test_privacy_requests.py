import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_authenticated_user_opens_tenant_scoped_access_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/privacy/requests',
            json={'request_type': 'access'},
            headers={'X-CSRF-Token': csrf},
        )
        assert response.status_code == 201, response.json()

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            """
                            select organization_id, subject_user_id, request_type, status
                            from data_subject_requests
                            where id = :request_id
                            """
                        ),
                        {'request_id': response.json()['id']},
                    )
                ).one()
                audit_event = await connection.scalar(
                    text(
                        """
                        select event_type from audit_events
                        where organization_id = :organization_id
                          and event_type = 'privacy.request.created'
                        """
                    ),
                    {'organization_id': context.organization_id},
                )
        finally:
            await owner.dispose()

    assert stored.organization_id == context.organization_id
    assert stored.subject_user_id == context.user_id
    assert stored.request_type == 'access'
    assert stored.status == 'pending'
    assert audit_event == 'privacy.request.created'


@pytest.mark.asyncio
async def test_admin_updates_privacy_request_with_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='admin') as context:
        csrf = context.login.cookies['saas_csrf']
        created = await context.client.post(
            '/api/v1/privacy/requests',
            json={'request_type': 'portability'},
            headers={'X-CSRF-Token': csrf},
        )
        response = await context.client.patch(
            f"/api/v1/privacy/requests/{created.json()['id']}",
            json={'status': 'completed', 'notes': 'Exportação entregue ao titular.'},
            headers={'X-CSRF-Token': csrf},
        )
        assert response.status_code == 200, response.json()

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            'select status, notes, completed_at from data_subject_requests '
                            'where id = :request_id'
                        ),
                        {'request_id': created.json()['id']},
                    )
                ).one()
                audit_event = await connection.scalar(
                    text(
                        "select event_type from audit_events "
                        "where target_id = :request_id "
                        "and event_type = 'privacy.request.updated'"
                    ),
                    {'request_id': created.json()['id']},
                )
        finally:
            await owner.dispose()

    assert stored.status == 'completed'
    assert stored.notes == 'Exportação entregue ao titular.'
    assert stored.completed_at is not None
    assert audit_event == 'privacy.request.updated'


@pytest.mark.asyncio
async def test_member_cannot_administer_privacy_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch, role='member') as context:
        csrf = context.login.cookies['saas_csrf']
        created = await context.client.post(
            '/api/v1/privacy/requests',
            json={'request_type': 'access'},
            headers={'X-CSRF-Token': csrf},
        )
        response = await context.client.patch(
            f"/api/v1/privacy/requests/{created.json()['id']}",
            json={'status': 'in_progress'},
            headers={'X-CSRF-Token': csrf},
        )
    assert response.status_code == 403
