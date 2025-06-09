from typing import Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserLogin(BaseModel):
    email: str
    password: str

class UserBaseModel(BaseModel):
    name: str
    email: str
    role : Literal["admin", "student", "org"]

class UserCreate(UserBaseModel):
    password: str

class PublicUserCreate(BaseModel):
    name: str
    email: str
    role: Literal["student", "org"]
    password: str

class UserUpdate(BaseModel):
    name: str | None  = None
    email: str | None = None
    password: str | None = None

class AdminUserUpdate(UserUpdate):
    role: Literal["admin", "user", "org"] | None = None
#response looks good
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    model_config = {
        "from_attributes": True
    }

class UserResponsePublic(BaseModel):
    id: int
    name: str
    role: str

    model_config = {
        "from_attributes": True
    }


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

#LIKES
class LikeBase(BaseModel):
    user_id: int
    event_id: int

#MEDIA
class MediaBase(BaseModel):
    event_id: int
    user_id: int | None = None
    type: Literal["image", "video"]

class MediaResponse(MediaBase):
    id: int
    url: str
    uploaded_at: datetime