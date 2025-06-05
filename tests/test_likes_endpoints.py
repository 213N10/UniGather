# tests/test_likes_endpoints.py

import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_like_unlike_flow(client):
    # 1) Register & login a user
    user = {
        "name": "liker_user",
        "email": "liker@example.com",
        "password": "likepass",
        "role": "student"
    }
    await client.post("/register", json=user)

    login_resp = await client.get(
        "/login",
        params={"email": user["email"], "password": user["password"]}
    )
    assert login_resp.status_code == 200
    headers = {"Authorization": "Bearer faketoken"}

    # 2) Create an event
    event_payload = {
        "title": "Like Test Event",
        "description": "Testing like endpoints",
        "location": "Likeville",
        "event_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "visibility": "public",
        "created_by": 1
    }
    event_resp = await client.post("/events", json=event_payload, headers=headers)
    assert event_resp.status_code == 200
    event_id = event_resp.json()["event_id"]

    # 3) Like the event
    like_payload = {"user_id": 1, "event_id": event_id}
    like_resp = await client.post("/likes", json=like_payload, headers=headers)
    assert like_resp.status_code == 200
    assert like_resp.json()["message"] == "Liked"

    # 4) Duplicate “like” → should fail (error)
    dup_like = await client.post("/likes", json=like_payload, headers=headers)
    assert dup_like.status_code == 200
    assert "error" in dup_like.json()

    # 5) GET likes for user
    get_resp = await client.get(f"/likes/1", headers=headers)
    assert get_resp.status_code == 200
    liked_list = get_resp.json()["likes"]
    # Should contain exactly one record
    assert isinstance(liked_list, list) and len(liked_list) == 1
    assert liked_list[0]["event_id"] == event_id and liked_list[0]["user_id"] == 1

    # 6) Unlike the event (use .request() to pass JSON on DELETE)
    unlike_resp = await client.request("DELETE", "/likes", json=like_payload, headers=headers)
    assert unlike_resp.status_code == 200
    assert unlike_resp.json()["message"] == "Unliked"

    # 7) GET again → list should now be empty
    get_after = await client.get(f"/likes/1", headers=headers)
    assert get_after.status_code == 200
    assert get_after.json()["likes"] == []

    # 8) Attempt to unlike again → should return “error”
    missing_unlike = await client.request("DELETE", "/likes", json=like_payload, headers=headers)
    assert missing_unlike.status_code == 200
    assert "error" in missing_unlike.json()
