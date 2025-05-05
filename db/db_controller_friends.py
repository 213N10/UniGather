from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_models import Friends
from api.api_objects import Friendship, FriendshipUpdate
from datetime import datetime


class FriendshipController:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def send_friend_request(self, friendship: Friendship) -> bool:
        # Sprawdzamy, czy już istnieje prośba o przyjaźń w jedną lub drugą stronę
        stmt = select(Friends).where(
            (Friends.user_id == friendship.user_id and Friends.friend_id == friendship.friend_id) |
            (Friends.user_id == friendship.friend_id and Friends.friend_id == friendship.user_id)
        )
        result = await self.db.execute(stmt)
        existing_request = result.scalars().first()

        if existing_request:
            return False  # Prośba już istnieje

        # Tworzymy nową prośbę o przyjaźń
        new_request = Friends(
            user_id=friendship.user_id,
            friend_id=friendship.friend_id,
            status=friendship.status,
            created_at=datetime.now()
        )
        self.db.add(new_request)
        await self.db.commit()
        await self.db.refresh(new_request)  # Upewniamy się, że ID jest dostępne
        return True

    async def update_friend_status(self, user_id: int, friend_id: int, status: str) -> bool:
        stmt = select(Friends).where(
            Friends.user_id == user_id,
            Friends.friend_id == friend_id
        )
        result = await self.db.execute(stmt)
        record = result.scalars().first()

        if record:
            record.status = status
            await self.db.commit()
            return True
        return False

    async def get_friends(self, user_id: int) -> List[Friends]:
        stmt = select(Friends).where(Friends.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_friend(self, user_id: int, friend_id: int) -> bool:
        stmt = select(Friends).where(
            Friends.user_id == user_id,
            Friends.friend_id == friend_id
        )
        result = await self.db.execute(stmt)
        record = result.scalars().first()

        if record:
            await self.db.delete(record)
            await self.db.commit()
            return True
        return False