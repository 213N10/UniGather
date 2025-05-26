from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_controller_likes import SESSION
from db.db_models import Media
from api.api_objects import MediaBase
from datetime import datetime





class MediaController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_media(self, media: MediaBase, url: str) -> int:
        # Sprawdzamy, czy media już istnieją dla tego wydarzenia (np. po URL lub typie)
        stmt = select(Media).where(
            Media.event_id == media.event_id,
            Media.url == url
        )
        result = await self.db.execute(stmt)
        existing_media = result.scalars().first()

        if existing_media:
            return existing_media.id  # Jeśli media już istnieją, zwróć ich ID

        # Tworzymy nowe media
        new_media = Media(
            event_id=media.event_id,
                user_id=media.user_id,
            type=media.type,
            url=url,
            uploaded_at=datetime.now()
        )
        self.db.add(new_media)
        await self.db.commit()
        await self.db.refresh(new_media)  # Upewniamy się, że ID jest dostępne
        return new_media.id

    async def get_media_for_event(self, event_id: int) -> List[Media]:
        stmt = select(Media).where(Media.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_media_for_user(self, user_id: int) -> List[Media]:
        stmt = select(Media).where(Media.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()



    async def delete_media(self, media_id: int) -> bool:
        media = await self.db.get(Media, media_id)
        if media:
            await self.db.delete(media)
            await self.db.commit()
            return True
        return False
