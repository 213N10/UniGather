# tests/test_attendance_endpoints.py

import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_attendance_crud_flow(client):
    # 1) Register & login a user
    user_payload = {
        "name": "attendee_user",
        "email": "attendee@example.com",
        "password": "pass1234",
        "role": "student"
    }
    # Register
    await client.post("/register", json=user_payload)
    # Login (we only care that login succeeds—no real token is returned)
    login_resp = await client.get(
        "/login",
        params={"email": user_payload["email"], "password": user_payload["password"]}
    )
    assert login_resp.status_code == 200
    # From here on, just send a dummy Bearer token in Authorization header
    headers = {"Authorization": "Bearer faketoken"}

    # 2) Create an event (so that we have an event_id)
    event_payload = {
        "title": "Attend Test Event",
        "description": "Testing attendance endpoints",
        "location": "Testville",
        "event_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "visibility": "public",
        "created_by": 1  # this user’s ID should be 1, since they are the first registered
    }
    event_resp = await client.post("/events", json=event_payload, headers=headers)
    assert event_resp.status_code == 200
    event_id = event_resp.json()["event_id"]

    # 3) Add attendance (first time → success)
    attend_payload = {"user_id": 1, "event_id": event_id, "status": "going"}
    add_resp = await client.post("/attendance", json=attend_payload, headers=headers)
    assert add_resp.status_code == 200
    assert add_resp.json()["message"] == "Attendance added"

    # 4) Attempt duplicate → should return an “error” key in JSON
    dup_resp = await client.post("/attendance", json=attend_payload, headers=headers)
    assert dup_resp.status_code == 200
    assert "error" in dup_resp.json()

    # 5) GET attendees by event
    get_by_event = await client.get(f"/attendance/event/{event_id}", headers=headers)
    assert get_by_event.status_code == 200
    attendees = get_by_event.json()
    assert isinstance(attendees, list) and len(attendees) == 1
    assert attendees[0]["user_id"] == 1 and attendees[0]["event_id"] == event_id

    # 6) GET attendance by user
    get_by_user = await client.get(f"/attendance/user/1", headers=headers)
    assert get_by_user.status_code == 200
    by_user = get_by_user.json()
    assert isinstance(by_user, list) and len(by_user) == 1
    assert by_user[0]["event_id"] == event_id

    # 7) DELETE the attendance
    del_resp = await client.delete(f"/attendance?user_id=1&event_id={event_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Attendance removed"

    # 8) GET again → should be empty list
    empty_resp = await client.get(f"/attendance/event/{event_id}", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []

    # 9) DELETE non‐existent → should return an “error” key
    del_missing = await client.delete(f"/attendance?user_id=1&event_id={event_id}", headers=headers)
    assert del_missing.status_code == 200
    assert "error" in del_missing.json()
