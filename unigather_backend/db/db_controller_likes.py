from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_models import Likes
from api.api_objects import LikeBase

class LikeController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_like(self, like: LikeBase) -> bool:
        new_like = Likes(
            user_id=like.user_id,
            event_id=like.event_id,
            created_at=datetime.now()
        )
        self.db.add(new_like)
        try:
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def remove_like(self, like: LikeBase) -> bool:
        stmt = select(Likes).where(
            Likes.user_id  == like.user_id,
            Likes.event_id == like.event_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            await self.db.delete(existing)
            await self.db.commit()
            return True
        return False

    async def get_likes_for_user(self, user_id: int) -> List[Likes]:
        stmt = select(Likes).where(Likes.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()