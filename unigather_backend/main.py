from fastapi import FastAPI, Depends
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from db.database import get_db
from db.db_controller_user import UserController
from db.db_controller_events import EventController
from db.db_controller_attendance import AttendanceController
from db.db_controller_comments import CommentController
from db.db_controller_friends import FriendshipController
from db.db_controller_media import MediaController

from db.db_controller_likes import db_add_like, db_delete_like, db_get_likes_for_user


from api.api_objects import UserCreate, UserUpdate
from api.api_objects import EventBase, EventUpdate
from api.api_objects import AttendanceBase
from api.api_objects import CommentBase
from api.api_objects import Friendship, FriendshipUpdate
from api.api_objects import MediaBase
from api.api_objects import LikeBase

tags_metadata = [
    {
        "name": "authentication",
        "description": "Authentications endpoints.",
    }, 
    
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "events",
        "description": "Manage events.",
    },
    {
        "name": "attendance",
        "description": "Operations with events attendance.",
    },
    {
        "name": "comments",
        "description": "Operations with user comments under events.",
    },
    {
        "name": "friends",
        "description": "Operations with users friends.",
    },
    {
        "name": "media",
        "description": "Operations with pictures uploaded for events.",
    },
    {
        "name": "health",
        "description": "Health check endpoint.",
    },
    
]

description = """
## APi created by Jan Zieniewicz and Khalid Muzaffar for the UniGather project.
### Jan Zieniewicz - 263930@student.pwr.edu.pl
### Khalid Muzaffar - 269553@student.pwr.edu.pl

# This API is used to manage users, events, attendance, comments, friends and media for the UniGather application.


"""


app = FastAPI(
    title="UniGather API",
    description=description,
    version="0.1.0",
    contact={
        "name": "Contact out developers",
        "description": "Contact developers for any isssues connected with the API.", 
        "email": "contact@unigather.com",
    },
    
    openapi_tags=tags_metadata
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/health", tags=["health"])
async def health_check(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"status": "healthy"}


#done
@app.get("/users", tags=["users"])
async def get_users(token: Annotated[str, Depends(oauth2_scheme)], name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.get_users(name, email, role)
    if not result:
        return {"message": "No users found", "users": []}
    return {"message": "Users found", "users": result} 
    
#done
@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.get_user_by_id(user_id)
    if result:
        return {"message": "User found", "user": result}
    else:
        return {"message": "User not found", "user": None}

@app.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    db_update_event = await service.update_user(user_id, user )
    if db_update_event:
        return {"message": "User updated", "user_id": user_id, "user": user}
    else:
        return {"message": "User couldnt be updated", "user_id": user_id, "user": None}

#done
@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.delete_user(user_id)
    service = UserController(db)
    if not result:
        return {"message": "User not found", "user_id": user_id}
    
    return {"message": "User deleted", "user_id": user_id}

#done
@app.post("/register", tags=["authentication"])
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.add_user(user)
    if result is None:
        return {"message": "User already exists", "user": None}
    user = await service.get_user_by_id(result)
    return {"message": "User created", "user": user}

#done
@app.get("/login", tags=["authentication"])
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.login_user(email, password)
    if not result:
        return {"message": "Invalid credentials", "user": None}
    
    return {"message": "Login successful", "user": result}


#Events
@app.post("/events", tags=["events"])
async def create_event(event: EventBase, db: AsyncSession = Depends(get_db)):
    service = EventController(db)
    event_id = await service.add_event(event)
    return {"message": "Event created", "event_id": event_id}

@app.get("/events", tags=["events"])
async def list_events(created_by: Optional[int] = None, visibility: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = EventController(db)
    result = await service.get_events(created_by, visibility)
    return result

@app.get("/events/{event_id}", tags=["events"])
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    service = EventController(db)
    result = await service.get_event_by_id(event_id)
    if result:
        return result
    return {"error": "Event not found"}

@app.put("/events/{event_id}", tags=["events"])
async def update_event(event_id: int, event: EventUpdate, db: AsyncSession = Depends(get_db)):
    service = EventController(db)
    success = await service.update_event(event_id, event)
    if success:
        return {"message": "Event updated"}
    return {"error": "Event not found"}

@app.delete("/events/{event_id}", tags=["events"])
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db)):
    service = EventController(db)
    success = await service.delete_event(event_id)
    if success:
        return {"message": "Event deleted"}
    return {"error": "Event not found"}

#Attendance
@app.post("/attendance", tags=["attendance"])
async def add_attendance(attendance: AttendanceBase, db: AsyncSession = Depends(get_db)):
    service = AttendanceController(db)
    result = await service.add_attendance(attendance)
    if result:
        return {"message": "Attendance added"}
    return {"error": "Could not add attendance"}

@app.get("/attendance/event/{event_id}", tags=["attendance"])
async def get_event_attendees(event_id: int, db: AsyncSession = Depends(get_db)):
    service = AttendanceController(db)
    result = await service.get_attendance_by_event(event_id)
    return result

@app.get("/attendance/user/{user_id}", tags=["attendance"])
async def get_user_attendance(user_id: int, db: AsyncSession = Depends(get_db)):
    service = AttendanceController(db)
    result = await service.get_attendance_by_user(user_id)
    return result

@app.delete("/attendance", tags=["attendance"])
async def delete_attendance(user_id: int, event_id: int, db: AsyncSession = Depends(get_db)):
    service = AttendanceController(db)
    result = await service.delete_attendance(user_id, event_id)
    if result:
        return {"message": "Attendance removed"}
    return {"error": "Record not found"}

#Comments
@app.post("/comments", tags=["comments"])
async def add_comment(comment: CommentBase, db: AsyncSession = Depends(get_db)):
    service = CommentController(db)
    comment_id = await service.add_comment(comment)
    return {"message": "Comment added", "comment_id": comment_id}

@app.get("/comments/{event_id}", tags=["comments"])
async def get_comments(event_id: int, db: AsyncSession = Depends(get_db)):
    service = CommentController(db)

    result = await service.get_comments_for_event(event_id)
    return result

@app.delete("/comments/{comment_id}", tags=["comments"])
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    service = CommentController(db)

    result = await service.delete_comment(comment_id)
    if result:
        return {"message": "Comment deleted"}
    return {"error": "Comment not found"}

#Friends
@app.post("/friends", tags=["friends"])
async def send_friend_request(friendship: Friendship, db: AsyncSession = Depends(get_db)):
    service = FriendshipController(db)
    result = await service.send_friend_request(friendship)
    return {"message": "Friend request sent" if result else "Failed to send request"}

@app.put("/friends/{user_id}/{friend_id}", tags=["friends"])
async def update_friend_status(user_id: int, friend_id: int, update: FriendshipUpdate, db: AsyncSession = Depends(get_db)):
    service = FriendshipController(db)
    result = await service.update_friend_status(user_id, friend_id, update.status)
    return {"message": "Friendship updated" if result else "Friendship not found"}

@app.get("/friends/{user_id}", tags=["friends"])
async def get_friends(user_id: int, db: AsyncSession = Depends(get_db)):
    service = FriendshipController(db)
    return await service.get_friends(user_id)

@app.delete("/friends/{user_id}/{friend_id}", tags=["friends"])
async def delete_friend(user_id: int, friend_id: int, db: AsyncSession = Depends(get_db)):
    service = FriendshipController(db)
    result = await service.delete_friend(user_id, friend_id)
    return {"message": "Friend removed" if result else "Friendship not found"}

#Media
@app.post("/media", tags=["media"])
async def add_media(media: MediaBase, url: str, db: AsyncSession = Depends(get_db)):
    service = MediaController(db)
    media_id = await service.add_media(media, url)
    return {"message": "Media added", "media_id": media_id}

@app.get("/media/{event_id}", tags=["media"])
async def get_event_media(event_id: int, db: AsyncSession = Depends(get_db)):
    service = MediaController(db)
    result = await service.get_media_for_event(event_id)
    return result


@app.delete("/media/{media_id}", tags=["media"])
async def delete_media(media_id: int, db: AsyncSession = Depends(get_db)):
    service = MediaController(db)
    result = await service.delete_media(media_id)

@app.get("/media/user/{user_id}", tags=["media"])
async def get_user_media(user_id: int, db: AsyncSession = Depends(get_db)):
    service = MediaController(db)
    result = await service.get_media_for_user(user_id)
    return result



#LIKES
@app.post("/likes")
async def add_like(like: LikeBase):
    result = await db_add_like(like)
    return {"message": "Liked"} if result else {"error": "Failed to like"}

@app.delete("/likes")
async def remove_like(like: LikeBase):
    result = await db_delete_like(like)
    return {"message": "Unliked"} if result else {"error": "Like not found"}

@app.get("/likes/{user_id}")
async def get_user_likes(user_id: int):
    result = await db_get_likes_for_user(user_id)
    return result