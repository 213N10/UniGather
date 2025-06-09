
import pytest
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models import Users, Events, Media
from api.api_objects import MediaBase
from db.db_controller_media import MediaController  


@pytest.mark.asyncio
async def test_add_media_and_prevent_duplicates(db_session: AsyncSession):
    """
    1) Create one user and one event.
    2) Call add_media(...) with a URL → returns a new media_id.
    3) Calling add_media(...) again with the same (event_id, url) → returns the same media_id.
    4) Verify exactly one Media row exists in the DB.
    """
    user = Users(
        name="Media User",
        email="mediauser@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="Media Test Event",
        description="Event for media tests",
        location="Somewhere",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = MediaController(db_session)
    media_payload = MediaBase(event_id=event.id, user_id=user.id, type="image")


    url = "https://example.com/photo1.png"
    first_id = await ctrl.add_media(media_payload, url)
    assert isinstance(first_id, int) and first_id > 0

    second_id = await ctrl.add_media(media_payload, url)
    assert second_id == first_id

    result = await db_session.execute(select(Media))
    all_rows = result.scalars().all()
    assert len(all_rows) == 1
    row = all_rows[0]
    assert row.id == first_id
    assert row.event_id == event.id
    assert row.user_id == user.id
    assert row.type == "image"
    assert row.url == url


@pytest.mark.asyncio
async def test_get_media_filters(db_session: AsyncSession):
    """
    1) Create two users and two events.
    2) Add multiple media records:
       - Two media for event1 by user1
       - One media for event1 by user2
       - One media for event2 by user1
    3) get_media_for_event(event1.id) should return exactly three rows.
    4) get_media_for_event(event2.id) should return exactly one row.
    5) get_media_for_user(user1.id) should return exactly three rows (two for event1 + one for event2).
    6) get_media_for_user(user2.id) should return exactly one row.
    """
    u1 = Users(
        name="User A",
        email="usera@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    u2 = Users(
        name="User B",
        email="userb@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([u1, u2])
    await db_session.commit()
    await db_session.refresh(u1)
    await db_session.refresh(u2)

    e1 = Events(
        title="Event One",
        description="First event",
        location="Loc1",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=u1.id,
        created_at=datetime.utcnow(),
    )
    e2 = Events(
        title="Event Two",
        description="Second event",
        location="Loc2",
        datetime=datetime.utcnow() + timedelta(days=2),
        visibility="public",
        created_by=u2.id,
        created_at=datetime.utcnow(),
    )
    db_session.add_all([e1, e2])
    await db_session.commit()
    await db_session.refresh(e1)
    await db_session.refresh(e2)

    ctrl = MediaController(db_session)

    id1 = await ctrl.add_media(MediaBase(event_id=e1.id, user_id=u1.id, type="image"), "url_e1_u1_1.png")
    id2 = await ctrl.add_media(MediaBase(event_id=e1.id, user_id=u1.id, type="video"), "url_e1_u1_2.mp4")
    id3 = await ctrl.add_media(MediaBase(event_id=e1.id, user_id=u2.id, type="image"), "url_e1_u2_1.png")
    id4 = await ctrl.add_media(MediaBase(event_id=e2.id, user_id=u1.id, type="video"), "url_e2_u1_1.mp4")

    list_e1 = await ctrl.get_media_for_event(e1.id)
    assert len(list_e1) == 3
    returned_ids_e1 = {m.id for m in list_e1}
    assert returned_ids_e1 == {id1, id2, id3}

    list_e2 = await ctrl.get_media_for_event(e2.id)
    assert len(list_e2) == 1
    assert list_e2[0].id == id4

    user1_list = await ctrl.get_media_for_user(u1.id)
    assert len(user1_list) == 3
    returned_ids_u1 = {m.id for m in user1_list}
    assert returned_ids_u1 == {id1, id2, id4}

    user2_list = await ctrl.get_media_for_user(u2.id)
    assert len(user2_list) == 1
    assert user2_list[0].id == id3


@pytest.mark.asyncio
async def test_delete_media(db_session: AsyncSession):
    """
    1) Create user + event + one media row.
    2) delete_media(existing_id) → True and record is removed.
    3) delete_media(same_id) again → False.
    4) delete_media(nonexistent_id) → False.
    """
    user = Users(
        name="DeleteMediaUser",
        email="deletemedia@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="DeleteMediaEvent",
        description="Event to delete media from",
        location="Anywhere",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    media_row = Media(
        event_id=event.id,
        user_id=user.id,
        type="image",
        url="to_be_deleted.png",
        uploaded_at=datetime.utcnow(),
    )
    db_session.add(media_row)
    await db_session.commit()
    await db_session.refresh(media_row)

    ctrl = MediaController(db_session)
    mid = media_row.id

    deleted = await ctrl.delete_media(mid)
    assert deleted is True

    result = await db_session.execute(select(Media).where(Media.id == mid))
    assert result.scalars().first() is None

    deleted_again = await ctrl.delete_media(mid)
    assert deleted_again is False

    nonexistent = await ctrl.delete_media(99999)
    assert nonexistent is False


@pytest.mark.asyncio
async def test_get_media_empty_lists(db_session: AsyncSession):
    """
    If no Media rows exist yet for a given event or user, both getters should return an empty list.
    """
    ctrl = MediaController(db_session)

    event_list = await ctrl.get_media_for_event(123456)
    assert isinstance(event_list, list) and event_list == []

    user_list = await ctrl.get_media_for_user(654321)
    assert isinstance(user_list, list) and user_list == []
