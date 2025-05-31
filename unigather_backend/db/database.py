from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator


engine = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Dependency dla FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session