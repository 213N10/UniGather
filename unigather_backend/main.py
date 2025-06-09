from fastapi import FastAPI, Depends, Form, HTTPException
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from db.database import get_db
from db.db_controller_user import UserController
from db.db_controller_events import EventController
from db.db_controller_attendance import AttendanceController
from db.db_controller_comments import CommentController
from db.db_controller_friends import FriendshipController
from db.db_controller_media import MediaController
from db.db_controller_likes import LikeController

from api.api_objects import UserLogin, UserResponse, UserResponsePublic, UserUpdate, PublicUserCreate, UserCreate
from api.api_objects import EventBase, EventUpdate
from api.api_objects import AttendanceBase
from api.api_objects import CommentBase
from api.api_objects import Friendship, FriendshipUpdate
from api.api_objects import MediaBase
from api.api_objects import LikeBase

from api.user_auth import oauth2_scheme, get_current_user, create_access_token
from fastapi.middleware.cors import CORSMiddleware
import os



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
        "name": "likes",
        "description": "Operations for liking/unliking events and fetching a user’s likes.",
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

load_dotenv()

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



@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

#CORS (Cross-Origin Requests, for linking the frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#done
@app.get("/users", tags=["users"])
async def get_users(current_user = Depends(get_current_user), name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.get_users(name, email, role)
    if not result:
        return {"message": "No users found", "users": []}
    users = [UserResponsePublic.model_validate(user) for user in result]
    return {"message": "Users found", "users": users} 
    
#done
@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int, current_user = Depends(get_current_user),  db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.get_user_by_id(user_id)
    if result:
        if result.id == current_user.id or current_user.role == "admin":
            user_data = UserResponse.model_validate(result)
        else:
            user_data = UserResponsePublic.model_validate(result)

        return {"message": "User found", "user": user_data}
    else:
        return {"message": "User not found", "user": None}

@app.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this user"
        )
    service = UserController(db)
    db_update_event = await service.update_user(user_id, user)
    if db_update_event:
        return {"message": "User updated", "user_id": user_id, "user": user}
    else:
        return {"message": "User couldnt be updated", "user_id": user_id, "user": None}

#done
@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this user"
        )
    service = UserController(db)
    result = await service.delete_user(user_id)
    if not result:
        return {"message": "User not found", "user_id": user_id}
        
    return {"message": "User deleted", "user_id": user_id}
    
        
#done
@app.post("/register", tags=["authentication"])
async def create_user(user: PublicUserCreate, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    user_create: UserCreate = UserCreate(**user.model_dump())
    result = await service.add_user(user_create)
    if result is None:
        return {"message": "User already exists", "user": None}
    user = await service.get_user_by_id(result)
    return {"message": "User created", "user": user}

#done
@app.post("/login", tags=["authentication"])
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserController(db)
    result = await service.login_user(request.email, request.password)
    if not result:
        return {"message": "Invalid credentials", "user": None}
    
    access_token = create_access_token(data={"sub": result.id})
    
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer", "user": result}

@app.post("/token", tags=["authentication"])
async def swagger_login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Swagger login endpoint to generate a token.
    This is used for testing purposes in the Swagger UI.
    """
    service = UserController(db)
    user = await service.login_user(email = username, password = password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}

#Events
@app.post("/events", tags=["events"])
async def create_event(event: EventBase, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = EventController(db)
    event_id = await service.add_event(event)
    return {"message": "Event created", "event_id": event_id}

@app.get("/events", tags=["events"])
async def list_events(created_by: Optional[int] = None, visibility: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = EventController(db)
    result = await service.get_events(created_by, visibility)
    return result

@app.get("/events/{event_id}", tags=["events"])
async def get_event(event_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = EventController(db)
    result = await service.get_event_by_id(event_id)
    if result:
        return result
    return {"error": "Event not found"}

@app.put("/events/{event_id}", tags=["events"])
async def update_event(event_id: int, event: EventUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = EventController(db)
    result = await service.get_event_by_id(event_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != "admin" and current_user.id != result.created_by:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this event"
        ) 
    
    success = await service.update_event(event_id, event)
    if success:
        return {"message": "Event updated"}
    return {"error": "Event not found"}

@app.delete("/events/{event_id}", tags=["events"])
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = EventController(db)
    event = await service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != "admin" and current_user.id != event.created_by:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this event")

    success = await service.delete_event(event_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete event")

    return {"message": "Event deleted"}

#Attendance
@app.post("/attendance", tags=["attendance"])
async def add_attendance(attendance: AttendanceBase, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if attendance.user_id != current_user.id or current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only add your own attendance"
        )
    service = AttendanceController(db)
    result = await service.add_attendance(attendance)
    if result:
        return {"message": "Attendance added"}
    return {"error": "Could not add attendance"}

@app.get("/attendance/event/{event_id}", tags=["attendance"])
async def get_event_attendees(event_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = AttendanceController(db)
    result = await service.get_attendance_by_event(event_id)
    return result

@app.get("/attendance/user/{user_id}", tags=["attendance"])
async def get_user_attendance(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = AttendanceController(db)
    result = await service.get_attendance_by_user(user_id)
    return result

@app.delete("/attendance", tags=["attendance"])
async def delete_attendance(user_id: int, event_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if user_id != current_user.id or current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own attendance"
        )
    
    service = AttendanceController(db)
    result = await service.delete_attendance(user_id, event_id)
    if result:
        return {"message": "Attendance removed"}
    return {"error": "Record not found"}

#Comments
@app.post("/comments", tags=["comments"])
async def add_comment(comment: CommentBase, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = CommentController(db)
    comment_id = await service.add_comment(comment)
    return {"message": "Comment added", "comment_id": comment_id}

@app.get("/comments/{event_id}", tags=["comments"])
async def get_comments(event_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = CommentController(db)

    result = await service.get_comments_for_event(event_id)
    return result

@app.delete("/comments/{comment_id}", tags=["comments"])
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = CommentController(db)
    comment = await service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.id != comment.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await service.delete_comment(comment_id)
    return {"message": "Comment deleted"}

#Friends
@app.post("/friends", tags=["friends"])
async def send_friend_request(friendship: Friendship, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = FriendshipController(db)
    result = await service.send_friend_request(friendship)
    return {"message": "Friend request sent" if result else "Failed to send request"}

@app.put("/friends/{user_id}/{friend_id}", tags=["friends"])
async def update_friend_status(user_id: int, friend_id: int, update: FriendshipUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this friendship")

    service = FriendshipController(db)
    result = await service.update_friend_status(user_id, friend_id, update.status)
    return {"message": "Friendship updated" if result else "Friendship not found"}

@app.get("/friends/{user_id}", tags=["friends"])
async def get_friends(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = FriendshipController(db)
    return await service.get_friends(user_id)

@app.delete("/friends/{user_id}/{friend_id}", tags=["friends"])
async def delete_friend(user_id: int, friend_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this friendship")

    service = FriendshipController(db)
    result = await service.delete_friend(user_id, friend_id)
    return {"message": "Friend removed" if result else "Friendship not found"}

#Media
@app.post("/media", tags=["media"])
async def add_media(media: MediaBase, url: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = MediaController(db)
    media_id = await service.add_media(media, url)
    return {"message": "Media added", "media_id": media_id}

@app.get("/media/{event_id}", tags=["media"])
async def get_event_media(event_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = MediaController(db)
    result = await service.get_media_for_event(event_id)
    return result


@app.delete("/media/{media_id}", tags=["media"])
async def delete_media(media_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = MediaController(db)
    media = await service.get_media_by_id(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if current_user.id != media.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this media")

    await service.delete_media(media_id)
    return {"message": "Media deleted"}

@app.get("/media/user/{user_id}", tags=["media"])
async def get_user_media(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    service = MediaController(db)
    result = await service.get_media_for_user(user_id)
    return result



#LIKES
@app.post("/likes", tags=["likes"])
async def add_like(
    like: LikeBase,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = LikeController(db)
    success = await service.add_like(like)
    if success:
        return {"message": "Liked"}
    return {"error": "Failed to like"}

@app.delete("/likes", tags=["likes"])
async def remove_like(
    like: LikeBase,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if like.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to remove this like")

    service = LikeController(db)
    success = await service.remove_like(like)
    if success:
        return {"message": "Unliked"}
    return {"error": "Like not found"}

@app.get("/likes/{user_id}", tags=["likes"])
async def get_user_likes(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = LikeController(db)
    likes = await service.get_likes_for_user(user_id)
    return {"message": "Likes retrieved", "likes": likes}