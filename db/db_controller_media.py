from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db_models import Media
from api.api_objects import MediaBase
from datetime import datetime

ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_media(media: MediaBase, url: str) -> int:
    async with SESSION() as session:
        async with session.begin():
            new_media = Media(
                event_id=media.event_id,
                type=media.type,
                url=url,
                uploaded_at=datetime.now()
            )
            session.add(new_media)
            await session.commit()
            return new_media.id

async def db_get_media_for_event(event_id: int) -> List[Media]:
    async with SESSION() as session:
        stmt = select(Media).where(Media.event_id == event_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def db_delete_media(media_id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            media = await session.get(Media, media_id)
            if media:
                await session.delete(media)
                await session.commit()
                return True
            return False
