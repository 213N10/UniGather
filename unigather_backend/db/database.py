from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()
DB_STRING = os.environ["DB_STRING"]


engine = create_async_engine(DB_STRING)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Dependency dla FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET search_path TO uni_gather"))
        yield session