from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from db.db_models import Likes
from api.api_objects import LikeBase
from datetime import datetime

ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_like(like: LikeBase) -> bool:
    async with SESSION() as session:
        async with session.begin():
            like_entry = Likes(
                user_id=like.user_id,
                event_id=like.event_id,
                created_at=datetime.now()
            )
            session.add(like_entry)
            await session.commit()
            return True

async def db_delete_like(like: LikeBase) -> bool:
    async with SESSION() as session:
        async with session.begin():
            stmt = select(Likes).where(
                Likes.user_id == like.user_id,
                Likes.event_id == like.event_id
            )
            result = await session.execute(stmt)
            existing = result.scalars().first()
            if existing:
                await session.delete(existing)
                await session.commit()
                return True
            return False

async def db_get_likes_for_user(user_id: int):
    async with SESSION() as session:
        stmt = select(Likes).where(Likes.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()
