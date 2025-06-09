from typing import List, Sequence
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models import Media
from api.api_objects import MediaBase

class MediaController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_media(self, media: MediaBase, url: str) -> int:
        # check for existing media by event_id + url
        stmt = select(Media).where(
            Media.event_id == media.event_id,
            Media.url == url
        )
        result = await self.db.execute(stmt)
        existing_media = result.scalars().first()
        if existing_media:
            return existing_media.id

        # create new media
        new_media = Media(
            event_id=media.event_id,
            user_id=media.user_id,
            type=media.type,
            url=url,
            uploaded_at=datetime.now()
        )
        self.db.add(new_media)
        await self.db.commit()
        await self.db.refresh(new_media)
        return new_media.id

    async def get_media_for_event(self, event_id: int) -> Sequence[Media]:
        stmt = select(Media).where(Media.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_media_for_user(self, user_id: int) -> Sequence[Media]:
        stmt = select(Media).where(Media.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_media(self, media_id: int) -> bool:
        media = await self.db.get(Media, media_id)
        if not media:
            return False
        await self.db.delete(media)
        await self.db.commit()
        return True
    
    async def get_media_by_id(self, media_id: int) -> Media | None:
        stmt = select(Media).where(Media.id == media_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()