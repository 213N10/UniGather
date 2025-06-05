# tests/test_comments_endpoints.py

import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_comment_crud_flow(client):
    # 1) Register & login a user
    user_payload = {
        "name": "commenter_user",
        "email": "commenter@example.com",
        "password": "commentpass",
        "role": "student"
    }
    await client.post("/register", json=user_payload)
    login_resp = await client.get(
        "/login",
        params={"email": user_payload["email"], "password": user_payload["password"]}
    )
    assert login_resp.status_code == 200
    headers = {"Authorization": "Bearer faketoken"}

    # 2) Create an event (so we can add comments)
    event_payload = {
        "title": "Comment Test Event",
        "description": "Testing comment endpoints",
        "location": "Commentland",
        "event_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "visibility": "public",
        "created_by": 1
    }
    event_resp = await client.post("/events", json=event_payload, headers=headers)
    assert event_resp.status_code == 200
    event_id = event_resp.json()["event_id"]

    # 3) Add a comment
    comment_payload = {"event_id": event_id, "user_id": 1, "content": "First comment!"}
    add_resp = await client.post("/comments", json=comment_payload, headers=headers)
    assert add_resp.status_code == 200
    data = add_resp.json()
    assert "comment_id" in data
    comment_id = data["comment_id"]

    # 4) GET comments for that event
    get_resp = await client.get(f"/comments/{event_id}", headers=headers)
    assert get_resp.status_code == 200
    comments = get_resp.json()
    assert isinstance(comments, list) and len(comments) == 1
    assert comments[0]["content"] == "First comment!"
    assert comments[0]["user_id"] == 1 and comments[0]["event_id"] == event_id

    # 5) DELETE the comment
    del_resp = await client.delete(f"/comments/{comment_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Comment deleted"

    # 6) GET again → should be empty list
    empty_resp = await client.get(f"/comments/{event_id}", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []
