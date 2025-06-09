
import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_media_crud_flow(client):
    user = {"name": "media_user", "email": "media@example.com", "password": "mediapass", "role": "student"}
    await client.post("/register", json=user)
    login_resp = await client.get("/login", params={"email": user["email"], "password": user["password"]})
    assert login_resp.status_code == 200
    headers = {"Authorization": "Bearer faketoken"}

    event_payload = {
        "title": "Media Test Event",
        "description": "Testing media endpoints",
        "location": "Medialand",
        "event_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "visibility": "public",
        "created_by": 1
    }
    event_resp = await client.post("/events", json=event_payload, headers=headers)
    assert event_resp.status_code == 200
    event_id = event_resp.json()["event_id"]

    media_payload = {"event_id": event_id, "user_id": 1, "type": "image"}
    url_1 = "https://example.com/photo1.png"
    add_resp = await client.post(f"/media?url={url_1}", json=media_payload, headers=headers)
    assert add_resp.status_code == 200
    media_id_1 = add_resp.json()["media_id"]

    add_dup = await client.post(f"/media?url={url_1}", json=media_payload, headers=headers)
    assert add_dup.status_code == 200
    assert add_dup.json()["media_id"] == media_id_1

    url_2 = "https://example.com/video2.mp4"
    media_payload["type"] = "video"
    add_resp2 = await client.post(f"/media?url={url_2}", json=media_payload, headers=headers)
    assert add_resp2.status_code == 200
    media_id_2 = add_resp2.json()["media_id"]
    assert media_id_2 != media_id_1

    get_event_media = await client.get(f"/media/{event_id}", headers=headers)
    assert get_event_media.status_code == 200
    event_media_list = get_event_media.json()
    assert isinstance(event_media_list, list) and len(event_media_list) == 2
    ids = {m["id"] for m in event_media_list}
    assert media_id_1 in ids and media_id_2 in ids

    get_user_media = await client.get(f"/media/user/1", headers=headers)
    assert get_user_media.status_code == 200
    user_media_list = get_user_media.json()
    assert isinstance(user_media_list, list) and len(user_media_list) == 2

    del_resp = await client.delete(f"/media/{media_id_1}", headers=headers)
    assert del_resp.status_code == 200

    get_event_after = await client.get(f"/media/{event_id}", headers=headers)
    assert get_event_after.status_code == 200
    after_list = get_event_after.json()
    assert isinstance(after_list, list) and len(after_list) == 1
    assert after_list[0]["id"] == media_id_2

    missing_del = await client.delete(f"/media/{media_id_1}", headers=headers)
    assert missing_del.status_code in (200, 404)
