import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_access_request_tables_use_rls_and_one_pending_request_per_email() -> None:
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(
                text(
                    """
                    select relname, relrowsecurity from pg_class
                    where relname in ('organization_access_links', 'access_requests')
                    order by relname
                    """
                )
            )
            assert rows.all() == [
                ('access_requests', True),
                ('organization_access_links', True),
            ]
            unique_index = await connection.scalar(
                text(
                    """
                    select count(*) from pg_indexes
                    where indexname = 'uq_access_requests_pending_email'
                      and indexdef ilike '%where%pending%'
                    """
                )
            )
            assert unique_index == 1
    finally:
        await engine.dispose()
