import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_audit_is_append_only_and_lgpd_requests_use_rls() -> None:
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(
                text(
                    """
                    select relname, relrowsecurity
                    from pg_class
                    where relname in ('audit_events', 'data_subject_requests')
                    order by relname
                    """
                )
            )
            assert rows.all() == [
                ('audit_events', True),
                ('data_subject_requests', True),
            ]
            privileges = await connection.execute(
                text(
                    """
                    select
                      has_table_privilege('gestao_de_funcionarios_app', 'audit_events', 'INSERT'),
                      has_table_privilege('gestao_de_funcionarios_app', 'audit_events', 'UPDATE'),
                      has_table_privilege('gestao_de_funcionarios_app', 'audit_events', 'DELETE')
                    """
                )
            )
            assert privileges.one() == (True, False, False)
    finally:
        await engine.dispose()
