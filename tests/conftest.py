

import os
import sys
import asyncio

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, PROJECT_ROOT)


import api.user_auth as _ua
_ua.hash_password = lambda pw: pw
_ua.verify_password = lambda plain, hashed: (plain == hashed)


from db.db_models import Base   


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@localhost/unigather_test"
)



@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()



@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    yield engine
    await engine.dispose()



@pytest_asyncio.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncSession:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = AsyncSessionLocal()

    try:
        yield session
    finally:
        await session.close()
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)



@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """
    Provides an httpx.AsyncClient against the FastAPI app in main.py,
    overriding get_db → yield our test-scoped db_session.
    """
    from main import app
    from db.database import get_db

    app.dependency_overrides[get_db] = lambda: db_session

 
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

  
    app.dependency_overrides.clear()
