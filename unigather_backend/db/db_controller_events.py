from typing import List, Optional, Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_models import Events
from api.api_objects import EventBase, EventUpdate
from datetime import datetime

class EventController:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def add_event(self, event: EventBase) -> Optional[int]:
        # Sprawdzamy, czy wydarzenie o takim tytule (lub innych unikalnych cechach) już istnieje
        stmt = select(Events).where(Events.title == event.title, Events.created_by == event.created_by)
        result = await self.db.execute(stmt)
        existing_event = result.scalars().first()

        if existing_event:
            return None  # Wydarzenie już istnieje

        # Jeśli nie istnieje, dodajemy nowe wydarzenie
        new_event = Events(
            title=event.title,
            description=event.description,
            location=event.location,
            datetime=event.event_datetime,
            visibility=event.visibility,
            created_by=event.created_by,
            created_at=datetime.now()
        )
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)  # Upewniamy się, że ID jest dostępne
        return new_event.id

    async def get_event_by_id(self, event_id: int) -> Optional[Events]:
        stmt = select(Events).where(Events.id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_events(self, created_by: Optional[int] = None, visibility: Optional[str] = None) -> Sequence[Events]:
        stmt = select(Events)

        if created_by:
            stmt = stmt.where(Events.created_by == created_by)
        if visibility:
            stmt = stmt.where(Events.visibility == visibility)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_event(self, event_id: int, event_data: EventUpdate) -> bool:
        event = await self.db.get(Events, event_id)
        if not event:
            return False

        if event_data.title is not None:
            event.title = event_data.title
        if event_data.description is not None:
            event.description = event_data.description
        if event_data.location is not None:
            event.location = event_data.location
        if event_data.event_datetime is not None:
            event.datetime = event_data.event_datetime
        if event_data.visibility is not None:
            event.visibility = event_data.visibility

        await self.db.commit()
        return True

    async def delete_event(self, event_id: int) -> bool:
        event = await self.db.get(Events, event_id)
        if not event:
            return False
        await self.db.delete(event)
        await self.db.commit()
        return True
