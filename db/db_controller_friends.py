from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db_models import Friends
from api.api_objects import Friendship, FriendshipUpdate
from datetime import datetime

ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_send_friend_request(friendship: Friendship) -> bool:
    async with SESSION() as session:
        async with session.begin():
            new_request = Friends(
                user_id=friendship.user_id,
                friend_id=friendship.friend_id,
                status=friendship.status,
                created_at=datetime.now()
            )
            session.add(new_request)
            await session.commit()
            return True

async def db_update_friend_status(user_id: int, friend_id: int, status: str) -> bool:
    async with SESSION() as session:
        async with session.begin():
            stmt = select(Friends).where(
                Friends.user_id == user_id,
                Friends.friend_id == friend_id
            )
            result = await session.execute(stmt)
            record = result.scalars().first()
            if record:
                record.status = status
                await session.commit()
                return True
            return False

async def db_get_friends(user_id: int) -> List[Friends]:
    async with SESSION() as session:
        stmt = select(Friends).where(Friends.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def db_delete_friend(user_id: int, friend_id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            stmt = select(Friends).where(
                Friends.user_id == user_id,
                Friends.friend_id == friend_id
            )
            result = await session.execute(stmt)
            record = result.scalars().first()
            if record:
                await session.delete(record)
                await session.commit()
                return True
            return False
