
import pytest
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_controller_attendance import AttendanceController
from db.db_models import Users, Events, Attendance
from api.api_objects import AttendanceBase


@pytest.mark.asyncio
async def test_add_and_get_attendance(db_session: AsyncSession):
    """
    1) Insert a dummy user and a dummy event.
    2) Add a new attendance record for (user_id, event_id) → should return True.
    3) Adding the same (user_id, event_id) again → should return False.
    4) get_attendance_by_event() and get_attendance_by_user() should each return exactly one record.
    """
    user = Users(
        name="Test User",
        email="testuser@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="Test Event",
        description="An event for testing",
        location="Test Location",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = AttendanceController(db_session)

    payload = AttendanceBase(
        user_id=user.id,
        event_id=event.id,
        status="interested"
    )
    added = await ctrl.add_attendance(payload)
    assert added is True

    duplicate = await ctrl.add_attendance(payload)
    assert duplicate is False

    event_list = await ctrl.get_attendance_by_event(event.id)
    assert isinstance(event_list, list)
    assert len(event_list) == 1
    rec = event_list[0]
    assert rec.user_id == user.id
    assert rec.event_id == event.id
    assert rec.status == "interested"

    user_list = await ctrl.get_attendance_by_user(user.id)
    assert isinstance(user_list, list)
    assert len(user_list) == 1
    rec2 = user_list[0]
    assert rec2.user_id == user.id
    assert rec2.event_id == event.id
    assert rec2.status == "interested"


@pytest.mark.asyncio
async def test_get_empty_attendance_lists(db_session: AsyncSession):
    """
    If no attendance rows exist for a given user_id or event_id,
    get_attendance_by_event / get_attendance_by_user should return an empty list.
    """
    user = Users(
        name="No Attend User",
        email="noattend@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="NoAttendEvent",
        description="No attendance should be here",
        location="Nowhere",
        datetime=datetime.utcnow() + timedelta(days=2),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = AttendanceController(db_session)

    assert (await ctrl.get_attendance_by_event(event.id)) == []
    assert (await ctrl.get_attendance_by_user(user.id)) == []


@pytest.mark.asyncio
async def test_delete_attendance(db_session: AsyncSession):
    """
    1) Insert a dummy user and event.
    2) Add one attendance, then delete it → should return True.
    3) After deletion, get_attendance_by_event & get_attendance_by_user both return empty.
    4) Trying to delete again returns False.
    """
    user = Users(
        name="Delete User",
        email="deleteuser@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="Delete Event",
        description="Event to delete attendance from",
        location="Somewhere",
        datetime=datetime.utcnow() + timedelta(days=3),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = AttendanceController(db_session)

    payload = AttendanceBase(
        user_id=user.id,
        event_id=event.id,
        status="going"
    )
    added = await ctrl.add_attendance(payload)
    assert added is True

    assert len(await ctrl.get_attendance_by_event(event.id)) == 1
    assert len(await ctrl.get_attendance_by_user(user.id)) == 1

    deleted = await ctrl.delete_attendance(user.id, event.id)
    assert deleted is True

    assert (await ctrl.get_attendance_by_event(event.id)) == []
    assert (await ctrl.get_attendance_by_user(user.id)) == []

    second_delete = await ctrl.delete_attendance(user.id, event.id)
    assert second_delete is False


@pytest.mark.asyncio
async def test_delete_nonexistent_attendance_returns_false(db_session: AsyncSession):
    """
    Attempting to delete an attendance record that never existed should return False.
    """
    
    user = Users(
        name="Never Attend User",
        email="never@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="NoOneAttends",
        description="Empty event",
        location="Anywhere",
        datetime=datetime.utcnow() + timedelta(days=5),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = AttendanceController(db_session)

    
    assert await ctrl.delete_attendance(user.id, event.id) is False
