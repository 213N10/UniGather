from fastapi import FastAPI
from typing import Optional

from db.db_controller_user import db_get_user_by_id, db_get_users, db_add_user, db_add_user, db_delete_user, db_delete_user,db_login_user
from db.db_controller_events import db_add_event, db_get_event_by_id, db_get_events,db_update_event, db_delete_event
from db.db_controller_attendance import db_add_attendance, db_get_attendance_by_event, db_get_attendance_by_user, db_delete_attendance
from db.db_controller_comments import db_add_comment, db_get_comments_for_event, db_delete_comment
from db.db_controller_friends import db_send_friend_request, db_update_friend_status, db_get_friends, db_delete_friend
from db.db_controller_media import db_add_media, db_get_media_for_event, db_delete_media

from api.api_objects import UserCreate
from api.api_objects import EventBase, EventUpdate
from api.api_objects import AttendanceBase
from api.api_objects import CommentBase
from api.api_objects import Friendship, FriendshipUpdate
from api.api_objects import MediaBase

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}



@app.get("/users")
async def get_users():
    result = await db_get_users()
    return result 
    

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    result = await db_get_user_by_id(user_id)
    if result:
        return result
    else:
        return {"error": "User not found"}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: dict):
    return {"message": "User updated", "user_id": user_id, "user": user}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    result = await db_delete_user(user_id)
    if not result:
        return {"error": "User not found"}
    
    return {"message": "User deleted", "user_id": user_id}


@app.post("/register")
async def create_user(user: UserCreate):
    result = await db_add_user(user)
    if not result:
        return {"message": "User already exists", "user": None}
    user = await db_get_user_by_id(result)
    return {"message": "User created", "user": user}


@app.get("/login")
async def login(email: str, password: str):
    # Implement your login logic here
    result = await db_login_user(email, password)
    if not result:
        return {"message": "Invalid credentials", "user": None}
    
    return {"message": "Login successful", "user": result}


#Events
@app.post("/events")
async def create_event(event: EventBase):
    event_id = await db_add_event(event)
    return {"message": "Event created", "event_id": event_id}

@app.get("/events")
async def list_events(created_by: Optional[int] = None, visibility: Optional[str] = None):
    result = await db_get_events(created_by, visibility)
    return result

@app.get("/events/{event_id}")
async def get_event(event_id: int):
    result = await db_get_event_by_id(event_id)
    if result:
        return result
    return {"error": "Event not found"}

@app.put("/events/{event_id}")
async def update_event(event_id: int, event: EventUpdate):
    success = await db_update_event(event_id, event)
    if success:
        return {"message": "Event updated"}
    return {"error": "Event not found"}

@app.delete("/events/{event_id}")
async def delete_event(event_id: int):
    success = await db_delete_event(event_id)
    if success:
        return {"message": "Event deleted"}
    return {"error": "Event not found"}

#Attendance
@app.post("/attendance")
async def add_attendance(attendance: AttendanceBase):
    result = await db_add_attendance(attendance)
    if result:
        return {"message": "Attendance added"}
    return {"error": "Could not add attendance"}

@app.get("/attendance/event/{event_id}")
async def get_event_attendees(event_id: int):
    result = await db_get_attendance_by_event(event_id)
    return result

@app.get("/attendance/user/{user_id}")
async def get_user_attendance(user_id: int):
    result = await db_get_attendance_by_user(user_id)
    return result

@app.delete("/attendance")
async def delete_attendance(user_id: int, event_id: int):
    result = await db_delete_attendance(user_id, event_id)
    if result:
        return {"message": "Attendance removed"}
    return {"error": "Record not found"}

#Comments
@app.post("/comments")
async def add_comment(comment: CommentBase):
    comment_id = await db_add_comment(comment)
    return {"message": "Comment added", "comment_id": comment_id}

@app.get("/comments/{event_id}")
async def get_comments(event_id: int):
    result = await db_get_comments_for_event(event_id)
    return result

@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int):
    result = await db_delete_comment(comment_id)
    if result:
        return {"message": "Comment deleted"}
    return {"error": "Comment not found"}

#Friends
@app.post("/friends")
async def send_friend_request(friendship: Friendship):
    result = await db_send_friend_request(friendship)
    return {"message": "Friend request sent" if result else "Failed to send request"}

@app.put("/friends/{user_id}/{friend_id}")
async def update_friend_status(user_id: int, friend_id: int, update: FriendshipUpdate):
    result = await db_update_friend_status(user_id, friend_id, update.status)
    return {"message": "Friendship updated" if result else "Friendship not found"}

@app.get("/friends/{user_id}")
async def get_friends(user_id: int):
    return await db_get_friends(user_id)

@app.delete("/friends/{user_id}/{friend_id}")
async def delete_friend(user_id: int, friend_id: int):
    result = await db_delete_friend(user_id, friend_id)
    return {"message": "Friend removed" if result else "Friendship not found"}

#Media
@app.post("/media")
async def add_media(media: MediaBase, url: str):
    media_id = await db_add_media(media, url)
    return {"message": "Media added", "media_id": media_id}

@app.get("/media/{event_id}")
async def get_event_media(event_id: int):
    result = await db_get_media_for_event(event_id)
    return result

@app.delete("/media/{media_id}")
async def delete_media(media_id: int):
    result = await db_delete_media(media_id)
    return {"message": "Media deleted"} if result else {"error": "Media not found"}
