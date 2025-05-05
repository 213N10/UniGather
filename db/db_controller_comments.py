from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.db_models import Comments
from api.api_objects import CommentBase
from datetime import datetime



class CommentController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_comment(self, comment: CommentBase) -> int:
        new_comment = Comments(
            event_id=comment.event_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=datetime.now()
        )
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)  # Upewniamy się, że ID jest dostępne
        return new_comment.id

    async def get_comments_for_event(self, event_id: int) -> List[Comments]:
        stmt = select(Comments).where(Comments.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_comment(self, comment_id: int) -> bool:
        comment = await self.db.get(Comments, comment_id)
        if comment:
            await self.db.delete(comment)
            await self.db.commit()
            return True
        return False
