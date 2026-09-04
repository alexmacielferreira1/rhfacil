import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_successful_login_writes_append_only_audit_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async with authenticated_client(monkeypatch) as context:
        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                event = (
                    await connection.execute(
                        text(
                            """
                            select event_type, actor_user_id, organization_id
                            from audit_events
                            where organization_id = :organization_id
                            """
                        ),
                        {'organization_id': context.organization_id},
                    )
                ).one_or_none()
        finally:
            await owner.dispose()

    assert event is not None
    assert event.event_type == 'auth.login.succeeded'
    assert event.actor_user_id == context.user_id
    assert event.organization_id == context.organization_id
