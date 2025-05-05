from typing import Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBaseModel(BaseModel):
    name: str
    email: str
    role : Literal["admin", "student", "org"]

class UserCreate(UserBaseModel):
    password: str

class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    password: str = None

class AdminUserUpdate(UserUpdate):
    role: Literal["admin", "user", "org"] = None
#response looks good
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime


#EVENTS
class EventBase(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    event_datetime: datetime
    visibility: Literal["public", "private"]
    created_by: int

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    event_datetime: datetime | None = None
    visibility: Literal["public", "private"] | None = None


class AttendanceBase(BaseModel):
    user_id: int
    event_id: int
    status: Literal["going", "interested", "not going"]  # możesz rozszerzyć listę


#API WILL RETURN COMMENTS FOR EVENT FROM DB
class CommentBase(BaseModel):
    event_id: int
    user_id: int
    content: str

class Friendship(BaseModel):
    user_id: int
    friend_id: int
    status: Literal["pending", "accepted", "blocked", "rejected"]

class FriendshipUpdate(BaseModel):
    status: Literal["pending", "accepted", "blocked", "rejected"]


class MediaBase(BaseModel):
    event_id: int
    type: Literal["image", "video"]

class MediaResponse(MediaBase):
    id: int
    url: str
    uploaded_at: datetime