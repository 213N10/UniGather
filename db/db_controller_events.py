from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db_models import Events
from api.api_objects import EventBase, EventUpdate
from datetime import datetime

# Reuse the same DB connection
ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_event(event: EventBase) -> int:
    async with SESSION() as session:
        async with session.begin():
            new_event = Events(
                title=event.title,
                description=event.description,
                location=event.location,
                datetime=event.event_datetime,
                visibility=event.visibility,
                created_by=event.created_by,
                created_at=datetime.now()
            )
            session.add(new_event)
            await session.commit()
            return new_event.id

async def db_get_event_by_id(event_id: int) -> Optional[Events]:
    async with SESSION() as session:
        stmt = select(Events).where(Events.id == event_id)
        result = await session.execute(stmt)
        return result.scalars().first()

async def db_get_events(created_by: Optional[int] = None, visibility: Optional[str] = None) -> List[Events]:
    async with SESSION() as session:
        stmt = select(Events)

        if created_by:
            stmt = stmt.where(Events.created_by == created_by)
        if visibility:
            stmt = stmt.where(Events.visibility == visibility)

        result = await session.execute(stmt)
        return result.scalars().all()

async def db_update_event(event_id: int, event_data: EventUpdate) -> bool:
    async with SESSION() as session:
        async with session.begin():
            event = await session.get(Events, event_id)
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

            await session.commit()
            return True

async def db_delete_event(event_id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            event = await session.get(Events, event_id)
            if not event:
                return False
            await session.delete(event)
            await session.commit()
            return True
