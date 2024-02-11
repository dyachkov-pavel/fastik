import asyncio
import os
from typing import Any
from typing import Generator

import asyncpg
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from db.session import get_db
from main import app
from settings import TEST_DATABASE_URL

# TEST_DATABASE_URL = "postgresql+asyncpg://ppp_test:111_test@127.0.0.1:5433/fastapi_test"

# test_engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)

test_async_session = sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

CLEAN_TABLES = [
    "users",
]


# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# @pytest.fixture(scope="session", autouse=True)
# async def run_migrations():
#     os.system("alembic init tests/migrations")
#     os.system('alembic revision --autogenerate -m "test running applications"')
#     os.system("alembic upgrade heads")


@pytest.fixture(scope="session")
async def async_session_test():
    # engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
    )
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"TRUNCATE TABLE {table_for_cleaning};"))


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """
    Create new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes
    """

    async def _get_test_db():
        try:
            yield test_async_session()
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        # "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
        "".join(TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool
    await pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE user_id = $1;""", user_id
            )

    return get_user_from_database_by_uuid
