

import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_friendship_crud_flow(client):
    alice = {"name": "Alice", "email": "alice@example.com", "password": "alicepass", "role": "student"}
    bob   = {"name": "Bob",   "email": "bob@example.com",   "password": "bobpass",   "role": "student"}

    await client.post("/register", json=alice)
    await client.post("/register", json=bob)

    login_resp = await client.get("/login", params={"email": alice["email"], "password": alice["password"]})
    assert login_resp.status_code == 200
    headers = {"Authorization": "Bearer faketoken"}

    fr_payload = {"user_id": 1, "friend_id": 2, "status": "pending"}
    send_resp = await client.post("/friends", json=fr_payload, headers=headers)
    assert send_resp.status_code == 200
    assert send_resp.json()["message"] == "Friend request sent"

    dup_resp = await client.post("/friends", json=fr_payload, headers=headers)
    assert dup_resp.status_code == 200
    assert "Failed" in dup_resp.json()["message"]

    login_bob = await client.get("/login", params={"email": bob["email"], "password": bob["password"]})
    assert login_bob.status_code == 200
    
    update_resp = await client.put("/friends/1/2", json={"status": "accepted"}, headers=headers)
    assert update_resp.status_code == 200
    assert "Friendship updated" in update_resp.json()["message"]

   
    get_resp = await client.get("/friends/1", headers=headers)
    assert get_resp.status_code == 200
    friends = get_resp.json()
    assert isinstance(friends, list)
    
    assert any(f["user_id"] == 1 and f["friend_id"] == 2 and f["status"] == "accepted" for f in friends)

   
    del_resp = await client.delete("/friends/1/2", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Friend removed"

    empty_resp = await client.get("/friends/1", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []
