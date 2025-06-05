# tests/test_comment_controller.py

import pytest
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models import Users, Events, Comments
from api.api_objects import CommentBase
from db.db_controller_comments import CommentController  # adjust import path as needed


@pytest.mark.asyncio
async def test_add_and_get_comments(db_session: AsyncSession):
    """
    1) Insert a dummy user and a dummy event.
    2) Call add_comment(...) → should return a new comment ID.
    3) Call get_comments_for_event(...) → should return exactly one row,
       and its fields should match what we inserted.
    """
    # STEP 1: Create a user
    user = Users(
        name="Commenter",
        email="comment@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # STEP 2: Create an event (must point to that same user.id)
    event = Events(
        title="Comment Event",
        description="Event used for comment tests",
        location="Here",
        datetime=datetime.utcnow() + timedelta(days=1),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = CommentController(db_session)

    # STEP 3: Add a comment
    payload = CommentBase(
        event_id=event.id,
        user_id=user.id,
        content="This is a test comment"
    )
    new_comment_id = await ctrl.add_comment(payload)
    assert isinstance(new_comment_id, int) and new_comment_id > 0

    # STEP 4: Retrieve via get_comments_for_event(...)
    comments = await ctrl.get_comments_for_event(event.id)
    assert isinstance(comments, list)
    assert len(comments) == 1

    comment_row = comments[0]
    assert comment_row.id == new_comment_id
    assert comment_row.event_id == event.id
    assert comment_row.user_id == user.id
    assert comment_row.content == "This is a test comment"


@pytest.mark.asyncio
async def test_get_empty_comments_list(db_session: AsyncSession):
    """
    If no comments exist for a given event, get_comments_for_event(...) should return [].
    """
    # Create a user + an event, but do NOT add any comment
    user = Users(
        name="NoCommentUser",
        email="nocomment@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="NoCommentsEvent",
        description="Event with no comments",
        location="Nowhere",
        datetime=datetime.utcnow() + timedelta(days=2),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = CommentController(db_session)

    comments = await ctrl.get_comments_for_event(event.id)
    assert isinstance(comments, list)
    assert comments == []


@pytest.mark.asyncio
async def test_delete_comment(db_session: AsyncSession):
    """
    1) Insert a user, event, and one comment.
    2) delete_comment(comment_id) → should return True.
    3) After deletion, get_comments_for_event(event.id) → [].
    4) delete_comment(same_id) again → should return False.
    """
    # STEP 1: Create a user and event
    user = Users(
        name="Deleter",
        email="delete@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    event = Events(
        title="DeleteCommentEvent",
        description="Event for delete_comment test",
        location="Anywhere",
        datetime=datetime.utcnow() + timedelta(days=3),
        visibility="public",
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    ctrl = CommentController(db_session)

    # STEP 2: Add a comment
    payload = CommentBase(
        event_id=event.id,
        user_id=user.id,
        content="Will be deleted"
    )
    comment_id = await ctrl.add_comment(payload)
    assert comment_id > 0

    # STEP 3: Delete it
    deleted = await ctrl.delete_comment(comment_id)
    assert deleted is True

    # STEP 4: Confirm that get_comments_for_event(...) is now empty
    comments_after = await ctrl.get_comments_for_event(event.id)
    assert comments_after == []

    # STEP 5: Attempt to delete the same comment again → False
    deleted_again = await ctrl.delete_comment(comment_id)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_delete_nonexistent_comment_returns_false(db_session: AsyncSession):
    """
    delete_comment(...) on an ID that was never inserted should return False.
    """
    ctrl = CommentController(db_session)

    # Choose an arbitrary ID that does not exist (e.g. 9999)
    result = await ctrl.delete_comment(9999)
    assert result is False
