from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.db_models import Attendance
from api.api_objects import AttendanceBase
from datetime import datetime



class AttendanceController:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def add_attendance(self, attendance: AttendanceBase) -> bool:
        # Sprawdź, czy rekord już istnieje
        stmt = select(Attendance).where(
            Attendance.user_id == attendance.user_id,
            Attendance.event_id == attendance.event_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            return False  # Użytkownik już zapisany

        # Jeśli nie istnieje, dodaj nowy rekord
        new_attendance = Attendance(
            user_id=attendance.user_id,
            event_id=attendance.event_id,
            status=attendance.status,
            timestamp=datetime.now()
        )
        self.db.add(new_attendance)
        await self.db.commit()
        return True

    async def get_attendance_by_event(self, event_id: int) -> Sequence[Attendance]:
        stmt = select(Attendance).where(Attendance.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_attendance_by_user(self, user_id: int) -> Sequence[Attendance]:
        stmt = select(Attendance).where(Attendance.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_attendance(self, user_id: int, event_id: int) -> bool:
        stmt = select(Attendance).where(
            Attendance.user_id == user_id,
            Attendance.event_id == event_id
        )
        result = await self.db.execute(stmt)
        attendance_record = result.scalars().first()
        if attendance_record:
            await self.db.delete(attendance_record)
            await self.db.commit()
            return True
        return False
