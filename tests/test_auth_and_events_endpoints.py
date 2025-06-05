# tests/test_auth_and_events_endpoints.py

import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    # 1) Register a new user → POST /register
    payload = {
        "name": "integration_user",
        "email": "intuser@example.com",
        "password": "supersecret123",
        "role": "student"
    }
    resp = await client.post("/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "User created"
    assert data["user"]["email"] == payload["email"]
    user_id = data["user"]["id"]

    # 2) Attempt duplicate registration → should indicate “User already exists”
    dup = await client.post("/register", json=payload)
    assert dup.status_code == 200
    dup_data = dup.json()
    assert dup_data["message"] == "User already exists"
    assert dup_data["user"] is None

    # 3) Log in → GET /login?email=...&password=...
    login_resp = await client.get(
        "/login",
        params={"email": payload["email"], "password": payload["password"]}
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["message"] == "Login successful"
    assert login_data["user"]["email"] == payload["email"]

    # 4) Fetch events list (no authentication required) → GET /events
    events_resp = await client.get("/events")
    assert events_resp.status_code == 200
    # Initially, no events exist, so expect an empty list
    assert events_resp.json() == []

    # 5) Create a new event → POST /events
    event_payload = {
        "title": "Integration Test Event",
        "description": "Testing event creation",
        "location": "Nowhere",
        "event_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "visibility": "public",
        "created_by": user_id
    }
    create_event_resp = await client.post("/events", json=event_payload)
    assert create_event_resp.status_code == 200
    ev_data = create_event_resp.json()
    assert ev_data["message"] == "Event created"
    event_id = ev_data["event_id"]

    # 6) Retrieve that specific event → GET /events/{event_id}
    get_event_resp = await client.get(f"/events/{event_id}")
    assert get_event_resp.status_code == 200
    fetched_event = get_event_resp.json()
    assert fetched_event["id"] == event_id
    assert fetched_event["title"] == event_payload["title"]

    # 7) Update the event → PUT /events/{event_id}
    update_payload = {"title": "Updated Test Event"}
    update_resp = await client.put(f"/events/{event_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["message"] == "Event updated"

    # 8) Delete the event → DELETE /events/{event_id}
    delete_resp = await client.delete(f"/events/{event_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Event deleted"

    # 9) Verify deletion → GET /events/{event_id} should return error
    missing_resp = await client.get(f"/events/{event_id}")
    assert missing_resp.status_code == 200
    assert missing_resp.json()["error"] == "Event not found"
