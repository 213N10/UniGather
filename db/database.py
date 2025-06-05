from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator


engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost/unigather")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Dependency dla FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session