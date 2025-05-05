from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db_models import Attendance
from api.api_objects import AttendanceBase
from datetime import datetime

ENGINE = create_async_engine("postgresql+asyncpg://postgres:0000@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_attendance(attendance: AttendanceBase) -> bool:
    async with SESSION() as session:
        async with session.begin():
            new_attendance = Attendance(
                user_id=attendance.user_id,
                event_id=attendance.event_id,
                status=attendance.status,
                timestamp=datetime.now()
            )
            session.add(new_attendance)
            await session.commit()
            return True

async def db_get_attendance_by_event(event_id: int) -> List[Attendance]:
    async with SESSION() as session:
        stmt = select(Attendance).where(Attendance.event_id == event_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def db_get_attendance_by_user(user_id: int) -> List[Attendance]:
    async with SESSION() as session:
        stmt = select(Attendance).where(Attendance.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def db_delete_attendance(user_id: int, event_id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            stmt = select(Attendance).where(
                Attendance.user_id == user_id,
                Attendance.event_id == event_id
            )
            result = await session.execute(stmt)
            attendance_record = result.scalars().first()
            if attendance_record:
                await session.delete(attendance_record)
                await session.commit()
                return True
            return False
