# tests/test_friendship_controller.py

import pytest
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models import Users, Friends
from api.api_objects import Friendship
from db.db_controller_friends import FriendshipController  # adjust import path if necessary


@pytest.mark.asyncio
async def test_send_friend_request_and_duplicates(db_session: AsyncSession):
    """
    1) Insert two dummy users.
    2) Call send_friend_request(...) → should return True.
    3) Calling send_friend_request again in the same direction → False.
    4) Calling send_friend_request in the reverse direction → False.
    5) Verify exactly one Friends row exists in the DB.
    """
    # STEP 1: Create two users
    user1 = Users(
        name="Alice",
        email="alice@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    user2 = Users(
        name="Bob",
        email="bob@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    ctrl = FriendshipController(db_session)

    # STEP 2: Send a friend request (user1 → user2)
    payload = Friendship(user_id=user1.id, friend_id=user2.id, status="pending")
    first_try = await ctrl.send_friend_request(payload)
    assert first_try is True, "First friend‐request should succeed"

    # STEP 3: Duplicate request in the same direction should fail
    second_try = await ctrl.send_friend_request(payload)
    assert second_try is False, "Duplicate request (same direction) should fail"

    # STEP 4: Reverse direction request (user2 → user1) should also fail
    reverse_payload = Friendship(user_id=user2.id, friend_id=user1.id, status="pending")
    reverse_try = await ctrl.send_friend_request(reverse_payload)
    assert reverse_try is False, "Duplicate request (reverse direction) should fail"

    # STEP 5: Exactly one entry in Friends table
    result = await db_session.execute(select(Friends))
    all_rows = result.scalars().all()
    assert len(all_rows) == 1
    row = all_rows[0]
    assert row.user_id == user1.id
    assert row.friend_id == user2.id
    assert row.status == "pending"


@pytest.mark.asyncio
async def test_update_friend_status(db_session: AsyncSession):
    """
    1) Insert two users and one Friends row (status="pending").
    2) Call update_friend_status(...) → should return True and update status to "accepted".
    3) Calling update_friend_status(...) on a non‐existent pair → False.
    """
    # STEP 1: Create two users and manually insert a Friends row
    user1 = Users(
        name="Charlie",
        email="charlie@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    user2 = Users(
        name="Dana",
        email="dana@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    # Insert a pending friendship (Charlie → Dana)
    friend_row = Friends(
        user_id=user1.id,
        friend_id=user2.id,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db_session.add(friend_row)
    await db_session.commit()
    await db_session.refresh(friend_row)

    ctrl = FriendshipController(db_session)

    # STEP 2: Update status to "accepted"
    updated = await ctrl.update_friend_status(user1.id, user2.id, "accepted")
    assert updated is True, "Existing friendship should be updated"

    # Confirm in DB:
    await db_session.refresh(friend_row)
    assert friend_row.status == "accepted"

    # STEP 3: Try updating non‐existent pair (e.g. user2 → user1)
    non_existent = await ctrl.update_friend_status(user2.id, user1.id, "accepted")
    assert non_existent is False


@pytest.mark.asyncio
async def test_get_friends_list(db_session: AsyncSession):
    """
    1) Insert one user (Alice) and three Friends rows:
       - Alice → Bob
       - Alice → Carol
       - Dave → Alice (should not appear when fetching for Alice)
    2) Call get_friends(user_id=Alice.id) → should return exactly two rows,
       for Bob and Carol.
    """
    # Create four users
    alice = Users(
        name="Alice",
        email="alice2@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    bob = Users(
        name="Bob",
        email="bob2@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    carol = Users(
        name="Carol",
        email="carol@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    dave = Users(
        name="Dave",
        email="dave@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([alice, bob, carol, dave])
    await db_session.commit()
    await db_session.refresh(alice)
    await db_session.refresh(bob)
    await db_session.refresh(carol)
    await db_session.refresh(dave)

    # Insert three friendship rows
    f1 = Friends(user_id=alice.id, friend_id=bob.id, status="accepted", created_at=datetime.utcnow())
    f2 = Friends(user_id=alice.id, friend_id=carol.id, status="accepted", created_at=datetime.utcnow())
    f3 = Friends(user_id=dave.id, friend_id=alice.id, status="accepted", created_at=datetime.utcnow())
    db_session.add_all([f1, f2, f3])
    await db_session.commit()
    await db_session.refresh(f1)
    await db_session.refresh(f2)
    await db_session.refresh(f3)

    ctrl = FriendshipController(db_session)

    # STEP 2: Fetch friends for Alice
    friends_list = await ctrl.get_friends(alice.id)
    assert isinstance(friends_list, list)

    # Expect exactly two rows (Bob and Carol)
    found_ids = {row.friend_id for row in friends_list}
    assert found_ids == {bob.id, carol.id}


@pytest.mark.asyncio
async def test_delete_friend(db_session: AsyncSession):
    """
    1) Insert two users and one Friends row.
    2) delete_friend(...) → True and row removed.
    3) delete_friend(...) again → False.
    """
    # STEP 1: Create users and a friendship
    user1 = Users(
        name="Eve",
        email="eve@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    user2 = Users(
        name="Frank",
        email="frank@example.com",
        password_hash="irrelevant",
        role="student",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    friend_row = Friends(
        user_id=user1.id,
        friend_id=user2.id,
        status="accepted",
        created_at=datetime.utcnow(),
    )
    db_session.add(friend_row)
    await db_session.commit()
    await db_session.refresh(friend_row)

    ctrl = FriendshipController(db_session)

    # STEP 2: Delete the friendship
    deleted = await ctrl.delete_friend(user1.id, user2.id)
    assert deleted is True

    # Confirm it’s removed:
    result = await db_session.execute(
        select(Friends).where(Friends.user_id == user1.id, Friends.friend_id == user2.id)
    )
    assert result.scalars().first() is None

    # STEP 3: Attempt to delete again → False
    deleted_again = await ctrl.delete_friend(user1.id, user2.id)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_delete_nonexistent_friend_returns_false(db_session: AsyncSession):
    """
    delete_friend(...) on a pair that was never inserted should return False.
    """
    ctrl = FriendshipController(db_session)
    result = await ctrl.delete_friend(12345, 67890)
    assert result is False
