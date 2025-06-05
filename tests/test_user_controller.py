import pytest
from sqlalchemy.exc import IntegrityError

from db.db_controller_user import UserController
from api.api_objects import UserCreate, UserUpdate

# We rely on the `db_session` fixture defined in tests/conftest.py

@pytest.mark.asyncio
async def test_add_and_get_user(db_session):
    """
    1. Add a new user via UserController.add_user()
    2. Retrieve it via get_user_by_id()
    3. Verify fields, then attempt to add duplicate email (should return None)
    """
    controller = UserController(db_session)

    # 1) Create a brand‐new user
    payload = UserCreate(
        name="Alice Test",
        email="alice@example.com",
        password="secure_password",
        role="student"
    )
    new_user_id = await controller.add_user(payload)
    assert isinstance(new_user_id, int)

    # 2) Fetch the user by ID
    user_obj = await controller.get_user_by_id(new_user_id)
    assert user_obj is not None
    assert user_obj.id == new_user_id
    assert user_obj.name == "Alice Test"
    assert user_obj.email == "alice@example.com"
    assert user_obj.role == "student"

    # 3) Attempt to create the same email again → should return None
    duplicate = await controller.add_user(payload)
    assert duplicate is None


@pytest.mark.asyncio
async def test_get_user_not_found(db_session):
    """
    Fetching a non‐existent user ID should return None.
    """
    controller = UserController(db_session)
    missing = await controller.get_user_by_id(9999)
    assert missing is None


@pytest.mark.asyncio
async def test_get_users_filtering(db_session):
    """
    Insert multiple users, then test get_users() with name/email/role filters.
    """
    ctrl = UserController(db_session)

    # Create three users
    u1_id = await ctrl.add_user(UserCreate(
        name="Bob", email="bob@example.com", password="pw", role="student"
    ))
    u2_id = await ctrl.add_user(UserCreate(
        name="Carol", email="carol@example.com", password="pw", role="admin"
    ))
    u3_id = await ctrl.add_user(UserCreate(
        name="Bobby", email="bobby@example.com", password="pw", role="student"
    ))

    # 1) get all students
    students = await ctrl.get_users(name=None, email=None, role="student")
    assert len(students) == 2
    returned_emails = {u.email for u in students}
    assert returned_emails == {"bob@example.com", "bobby@example.com"}

    # 2) filter by name substring "Bob"
    bobs = await ctrl.get_users(name="Bob", email=None, role=None)
    assert len(bobs) == 2
    assert {u.name for u in bobs} == {"Bob", "Bobby"}

    # 3) filter by exact email
    one = await ctrl.get_users(name=None, email="carol@example.com", role=None)
    assert len(one) == 1
    assert one[0].name == "Carol"


@pytest.mark.asyncio
async def test_update_user(db_session):
    """
    Create a user; update its name. Verify changes.
    Trying to update a non‐existent user returns False.
    """
    ctrl = UserController(db_session)
    # 1) Create a fresh user
    uid = await ctrl.add_user(UserCreate(
        name="Derek", email="derek@example.com", password="pw", role="student"
    ))

    # 2) Update name only.  Because UserUpdate does not allow email=None or password=None,
    #    we simply pass the existing email/password if we don’t want to change them.
    update_payload = UserUpdate(
        name="Derrick Updated",
        email="derek@example.com",
        password="pw"
    )
    success = await ctrl.update_user(uid, update_payload)
    assert success is True

    updated = await ctrl.get_user_by_id(uid)
    assert updated.name == "Derrick Updated"
    # Role should be unchanged (we never touched role)
    assert updated.role == "student"

    # 3) Try updating a non‐existent user → should return False
    bad = await ctrl.update_user(9999, update_payload)
    assert bad is False


@pytest.mark.asyncio
async def test_delete_user_and_login(db_session):
    """
    Test deleting a user and login behavior (correct & incorrect passwords).
    """
    ctrl = UserController(db_session)

    # 1) Create a user
    uid = await ctrl.add_user(UserCreate(
        name="Eve", email="eve@example.com", password="secret", role="student"
    ))

    # 2) Successful login
    logged_in = await ctrl.login_user(email="eve@example.com", password="secret")
    assert logged_in is not None
    assert logged_in.email == "eve@example.com"

    # 3) Wrong password → login_user returns None
    bad_login = await ctrl.login_user(email="eve@example.com", password="wrongpass")
    assert bad_login is None

    # 4) Delete the user
    deleted = await ctrl.delete_user(uid)
    assert deleted is True

    # 5) After deletion, fetch by ID should return None
    assert await ctrl.get_user_by_id(uid) is None

    # 6) And login should now fail
    assert await ctrl.login_user(email="eve@example.com", password="secret") is None

    # 7) Deleting again returns False
    assert await ctrl.delete_user(uid) is False
