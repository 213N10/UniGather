

import pytest
from datetime import datetime, timedelta

from db.db_models import Users
from db.db_controller_events import EventController
from api.api_objects import EventBase, EventUpdate


@pytest.mark.asyncio
async def test_add_and_get_event(db_session):
    """
    1) Insert a dummy user so that `created_by` is valid.
    2) Add a new event via EventController.add_event()
    3) Retrieve it via get_event_by_id()
    4) Verify fields, then attempt to add a duplicate (same title + creator) → should return None
    """
    dummy_user = Users(
        name="Dummy User",
        email="dummy1@example.com",
        password_hash="fakehash",
        role="student"
    )
    db_session.add(dummy_user)
    await db_session.commit()
    await db_session.refresh(dummy_user)
    user_id = dummy_user.id

    controller = EventController(db_session)

    now = datetime.utcnow()
    payload = EventBase(
        title="Test Event",
        description="A short description",
        location="Test Location",
        event_datetime=now + timedelta(days=1),
        visibility="public",
        created_by=user_id
    )
    new_event_id = await controller.add_event(payload)
    assert isinstance(new_event_id, int)

    ev = await controller.get_event_by_id(new_event_id)
    assert ev is not None
    assert ev.id == new_event_id
    assert ev.title == "Test Event"
    assert ev.description == "A short description"
    assert ev.location == "Test Location"
    assert ev.datetime == payload.event_datetime
    assert ev.visibility == "public"
    assert ev.created_by == user_id

    duplicate = await controller.add_event(payload)
    assert duplicate is None


@pytest.mark.asyncio
async def test_get_event_not_found(db_session):
    """
    Fetching a non-existent event ID should return None.
    (No need to insert a user here, since we're not inserting any event.)
    """
    controller = EventController(db_session)
    missing = await controller.get_event_by_id(9999)
    assert missing is None


@pytest.mark.asyncio
async def test_get_events_filtering(db_session):
    """
    1) Insert two dummy users so that `created_by` values are valid.
    2) Insert three events, then test get_events() filtering by created_by and visibility.
    """
    user1 = Users(
        name="User One",
        email="user1@example.com",
        password_hash="fakehash1",
        role="student"
    )
    user2 = Users(
        name="User Two",
        email="user2@example.com",
        password_hash="fakehash2",
        role="student"
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    ctrl = EventController(db_session)
    now = datetime.utcnow()

    e1 = EventBase(
        title="Alpha",
        description="Desc A",
        location="Loc A",
        event_datetime=now + timedelta(days=1),
        visibility="public",
        created_by=user1.id
    )
    e2 = EventBase(
        title="Beta",
        description="Desc B",
        location="Loc B",
        event_datetime=now + timedelta(days=2),
        visibility="private",
        created_by=user1.id
    )
    e3 = EventBase(
        title="Gamma",
        description="Desc C",
        location="Loc C",
        event_datetime=now + timedelta(days=3),
        visibility="public",
        created_by=user2.id
    )

    id1 = await ctrl.add_event(e1)
    id2 = await ctrl.add_event(e2)
    id3 = await ctrl.add_event(e3)

    all_events = await ctrl.get_events()
    assert len(all_events) == 3
    titles = {ev.title for ev in all_events}
    assert titles == {"Alpha", "Beta", "Gamma"}

    by_user1 = await ctrl.get_events(created_by=user1.id, visibility=None)
    assert len(by_user1) == 2
    assert {ev.title for ev in by_user1} == {"Alpha", "Beta"}

    public_only = await ctrl.get_events(created_by=None, visibility="public")
    assert len(public_only) == 2
    assert {ev.title for ev in public_only} == {"Alpha", "Gamma"}

    combo = await ctrl.get_events(created_by=user1.id, visibility="public")
    assert len(combo) == 1
    assert combo[0].title == "Alpha"


@pytest.mark.asyncio
async def test_update_event(db_session):
    """
    1) Insert a dummy user so that `created_by` is valid.
    2) Create an event, then update its fields. Verify changes.
    3) Trying to update a non-existent event returns False.
    """
    
    dummy_user = Users(
        name="Dummy Two",
        email="dummy2@example.com",
        password_hash="fakehash2",
        role="admin"
    )
    db_session.add(dummy_user)
    await db_session.commit()
    await db_session.refresh(dummy_user)

    ctrl = EventController(db_session)
    now = datetime.utcnow()


    payload = EventBase(
        title="Original Title",
        description="Original Desc",
        location="Original Loc",
        event_datetime=now + timedelta(days=1),
        visibility="public",
        created_by=dummy_user.id
    )
    eid = await ctrl.add_event(payload)
    assert isinstance(eid, int)

    update_payload = EventUpdate(
        title="Updated Title",
        description=None,
        location=None,
        event_datetime=None,
        visibility="private"
    )
    success = await ctrl.update_event(eid, update_payload)
    assert success is True

    updated = await ctrl.get_event_by_id(eid)
    assert updated.title == "Updated Title"
    assert updated.visibility == "private"
    assert updated.description == "Original Desc"
    assert updated.location == "Original Loc"
    assert updated.datetime == payload.event_datetime

    bad = await ctrl.update_event(9999, update_payload)
    assert bad is False


@pytest.mark.asyncio
async def test_delete_event(db_session):
    """
    1) Insert a dummy user so that `created_by` is valid.
    2) Create an event, then delete it. Verify deletion.
    3) Deleting a non-existent event should return False.
    """
    dummy_user = Users(
        name="Dummy Three",
        email="dummy3@example.com",
        password_hash="fakehash3",
        role="student"
    )
    db_session.add(dummy_user)
    await db_session.commit()
    await db_session.refresh(dummy_user)

    ctrl = EventController(db_session)
    now = datetime.utcnow()

    payload = EventBase(
        title="To Be Deleted",
        description="Will vanish",
        location="Nowhere",
        event_datetime=now + timedelta(days=1),
        visibility="public",
        created_by=dummy_user.id
    )
    eid = await ctrl.add_event(payload)
    assert isinstance(eid, int)

    deleted = await ctrl.delete_event(eid)
    assert deleted is True

    assert await ctrl.get_event_by_id(eid) is None

    assert await ctrl.delete_event(eid) is False
