from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()
DB_STRING = os.environ["DB_STRING"]


#engine = create_async_engine(DB_STRING)

# Load environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
SCHEMA = os.getenv("schema")


DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
engine = create_async_engine(DATABASE_URL, connect_args={"ssl": "require"}, poolclass=NullPool)
#print(f"Connecting to database at {DATABASE_URL}")



AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        text_schema = f"SET search_path TO {SCHEMA}"
        await session.execute(text(text_schema))
        yield session