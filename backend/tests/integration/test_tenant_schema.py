import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_tenant_tables_enable_row_level_security() -> None:
    engine = create_async_engine(os.environ['DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(
                text(
                    """
                    select relname, relrowsecurity
                    from pg_class
                    where relname in ('memberships', 'invitations', 'user_sessions')
                    order by relname
                    """
                )
            )
            assert rows.all() == [
                ('invitations', True),
                ('memberships', True),
                ('user_sessions', True),
            ]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_runtime_role_cannot_read_another_tenant() -> None:
    owner_url = os.environ['MIGRATION_DATABASE_URL']
    app_url = os.environ['DATABASE_URL']
    owner = create_async_engine(owner_url)
    runtime = create_async_engine(app_url)
    organization_a, organization_b, user_id = uuid4(), uuid4(), uuid4()
    try:
        async with owner.begin() as connection:
            await connection.execute(
                text(
                    "insert into organizations (id, name, slug) values "
                    "(:a, 'Tenant A', :slug_a), (:b, 'Tenant B', :slug_b)"
                ),
                {
                    'a': organization_a,
                    'b': organization_b,
                    'slug_a': f'a-{organization_a}',
                    'slug_b': f'b-{organization_b}',
                },
            )
            await connection.execute(
                text("insert into users (id, email, password_hash) values (:id, :email, 'test')"),
                {'id': user_id, 'email': f'{user_id}@example.test'},
            )
            await connection.execute(
                text(
                    "insert into memberships (organization_id, user_id, role) "
                    "values (:a, :user, 'member'), (:b, :user, 'member')"
                ),
                {'a': organization_a, 'b': organization_b, 'user': user_id},
            )

        async with runtime.begin() as connection:
            await connection.execute(
                text("select set_config('app.current_tenant_id', :tenant, true)"),
                {'tenant': str(organization_a)},
            )
            visible = await connection.scalar(text('select count(*) from memberships'))
            foreign = await connection.scalar(
                text('select count(*) from memberships where organization_id = :tenant'),
                {'tenant': organization_b},
            )
        assert visible == 1
        assert foreign == 0
    finally:
        async with owner.begin() as connection:
            await connection.execute(text('delete from users where id = :id'), {'id': user_id})
            await connection.execute(
                text('delete from organizations where id in (:a, :b)'),
                {'a': organization_a, 'b': organization_b},
            )
        await runtime.dispose()
        await owner.dispose()
