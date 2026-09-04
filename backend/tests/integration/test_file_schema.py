import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_stored_files_are_tenant_scoped_and_quarantined_by_default() -> None:
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            row = (
                await connection.execute(
                    text(
                        """
                        select c.relrowsecurity,
                               pg_get_expr(d.adbin, d.adrelid) as status_default
                        from pg_class c
                        join pg_attribute a on a.attrelid = c.oid and a.attname = 'status'
                        join pg_attrdef d on d.adrelid = c.oid and d.adnum = a.attnum
                        where c.relname = 'stored_files'
                        """
                    )
                )
            ).one()
        assert row.relrowsecurity is True
        assert 'quarantined' in row.status_default
    finally:
        await engine.dispose()
