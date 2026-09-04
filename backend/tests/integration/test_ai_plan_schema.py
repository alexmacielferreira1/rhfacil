import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_ai_usage_and_plan_tables_are_tenant_scoped() -> None:
    engine = create_async_engine(os.environ['MIGRATION_DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(
                text(
                    """
                    select relname, relrowsecurity
                    from pg_class
                    where relname in ('tenant_plans', 'ai_usage_events')
                    order by relname
                    """
                )
            )
            assert rows.all() == [
                ('ai_usage_events', True),
                ('tenant_plans', True),
            ]
            prompt_column = await connection.scalar(
                text(
                    """
                    select count(*) from information_schema.columns
                    where table_name = 'ai_usage_events'
                      and column_name in ('prompt', 'response', 'content')
                    """
                )
            )
            assert prompt_column == 0
    finally:
        await engine.dispose()
