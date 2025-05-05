from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db_models import Comments
from api.api_objects import CommentBase
from datetime import datetime

ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_comment(comment: CommentBase) -> int:
    async with SESSION() as session:
        async with session.begin():
            new_comment = Comments(
                event_id=comment.event_id,
                user_id=comment.user_id,
                content=comment.content,
                created_at=datetime.now()
            )
            session.add(new_comment)
            await session.commit()
            return new_comment.id

async def db_get_comments_for_event(event_id: int) -> List[Comments]:
    async with SESSION() as session:
        stmt = select(Comments).where(Comments.event_id == event_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def db_delete_comment(comment_id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            comment = await session.get(Comments, comment_id)
            if comment:
                await session.delete(comment)
                await session.commit()
                return True
            return False
