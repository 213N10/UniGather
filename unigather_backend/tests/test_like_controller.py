
import pytest
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from db.db_controller_likes import LikeController
from db.db_models import Users, Events
from api.api_objects import LikeBase


@pytest.mark.asyncio
async def test_add_and_remove_like_sequence(db_session: AsyncSession):
    """
    1) Insert a dummy user and a dummy event.
    2) Call add_like(...) → should return True.
    3) Calling add_like(...) again for the same (user_id, event_id)
       → should return False.
    4) Now call remove_like(...) → should return True (exactly one row existed).
    5) A second remove_like(...) → should return False (row already deleted).
    """
    user = Users(
        name="Like User",
        email="likeuser@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="Like Event",
        description="Event for like tests",
        location="Somewhere",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = LikeController(db_session)

    payload = LikeBase(user_id=user.id, event_id=event.id)
    first_add = await ctrl.add_like(payload)
    assert first_add is True, "The very first add_like(...) must return True"

    second_add = await ctrl.add_like(payload)
    assert second_add is False, "A duplicate add_like(...) must return False"

    first_remove = await ctrl.remove_like(payload)
    assert first_remove is True, "Since exactly one row existed, remove_like(...) must return True"

    second_remove = await ctrl.remove_like(payload)
    assert second_remove is False, "After deletion, remove_like(...) must return False"


@pytest.mark.asyncio
async def test_remove_like_when_none_exists(db_session: AsyncSession):
    """
    If no Likes exist at all for (user, event), remove_like(...) should immediately return False.
    """
    user = Users(
        name="Never Like User",
        email="neverlike@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="NeverLikeEvent",
        description="Event with no likes",
        location="SomewhereElse",
        datetime=datetime.utcnow() + timedelta(days=5),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = LikeController(db_session)

    payload = LikeBase(user_id=user.id, event_id=event.id)
    assert await ctrl.remove_like(payload) is False, (
        "If no row was ever inserted, remove_like(...) must return False"
    )

@pytest.mark.asyncio
async def test_get_likes_for_user_returns_exactly_one_row(db_session: AsyncSession):
    user = Users(
        name="Fetcher User",
        email="fetch@example.com",
        password_hash="dummyhash",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="Fetcher Event",
        description="Event for get_likes_for_user test",
        location="Anywhere",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = LikeController(db_session)

    payload = LikeBase(user_id=user.id, event_id=event.id)
    assert await ctrl.add_like(payload) is True

    likes_list = await ctrl.get_likes_for_user(user.id)
    assert isinstance(likes_list, list)
    assert len(likes_list) == 1

    like_row = likes_list[0]
    assert like_row.user_id == user.id
    assert like_row.event_id == event.id