# tests/test_attendance_controller.py

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
    # STEP 1: Insert a dummy user
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

    # STEP 2: Insert a dummy event (created_by must refer to that same user.id)
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

    # Now we have user.id and event.id
    ctrl = AttendanceController(db_session)

    # STEP 3: Add attendance for (user.id, event.id)
    payload = AttendanceBase(
        user_id=user.id,
        event_id=event.id,
        status="interested"
    )
    added = await ctrl.add_attendance(payload)
    assert added is True

    # Attempting to add the same (user_id, event_id) again should return False
    duplicate = await ctrl.add_attendance(payload)
    assert duplicate is False

    # STEP 4: get_attendance_by_event(event.id) → should return exactly one Attendance
    event_list = await ctrl.get_attendance_by_event(event.id)
    assert isinstance(event_list, list)
    assert len(event_list) == 1
    rec = event_list[0]
    assert rec.user_id == user.id
    assert rec.event_id == event.id
    assert rec.status == "interested"

    # get_attendance_by_user(user.id) → should similarly return exactly one
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
    # Insert a dummy user and event, but do not add any attendance
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

    # There is no attendance record yet for user.id / event.id
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
    # STEP 1: Insert user + event
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

    # STEP 2: Add attendance and then delete it
    payload = AttendanceBase(
        user_id=user.id,
        event_id=event.id,
        status="going"
    )
    added = await ctrl.add_attendance(payload)
    assert added is True

    # Verify it appears
    assert len(await ctrl.get_attendance_by_event(event.id)) == 1
    assert len(await ctrl.get_attendance_by_user(user.id)) == 1

    # Delete that attendance
    deleted = await ctrl.delete_attendance(user.id, event.id)
    assert deleted is True

    # After deletion, both lists should be empty
    assert (await ctrl.get_attendance_by_event(event.id)) == []
    assert (await ctrl.get_attendance_by_user(user.id)) == []

    # STEP 3: Delete again → should return False
    second_delete = await ctrl.delete_attendance(user.id, event.id)
    assert second_delete is False


@pytest.mark.asyncio
async def test_delete_nonexistent_attendance_returns_false(db_session: AsyncSession):
    """
    Attempting to delete an attendance record that never existed should return False.
    """
    # Create one user + event, but do NOT add an attendance record
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

    # No attendance was ever inserted → delete should return False
    assert await ctrl.delete_attendance(user.id, event.id) is False
