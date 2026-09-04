import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_migration_creates_schema_version() -> None:
    engine = create_async_engine(os.environ['DATABASE_URL'])
    try:
        async with engine.connect() as connection:
            exists = await connection.scalar(
                text("select to_regclass('public.app_schema_version')")
            )
        assert exists == 'app_schema_version'
    finally:
        await engine.dispose()
