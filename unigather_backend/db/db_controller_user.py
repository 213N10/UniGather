from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.api_objects import UserCreate, UserUpdate, AdminUserUpdate
from db.db_models import Users
from api.user_auth import hash_password, verify_password


class UserController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_user(self, user: UserCreate) -> Optional[int]:
        result = await self.db.execute(
            select(Users).where(Users.email == user.email)
        )
        if result.scalars().first():
            return None

        new_user = Users(
            name=user.name,
            email=user.email,
            password_hash=hash_password(user.password),
            role=user.role
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user.id
        
    async def update_user(self, id: int, user: UserUpdate) -> bool:
        user_to_update = await self.db.get(Users, id)
        if not user_to_update:
            return False

        if user.name:
            user_to_update.name = user.name
        if user.email:
            user_to_update.email = user.email
        if user.password:
            user_to_update.password_hash = hash_password(user.password)

        await self.db.commit()
        return True
        

    async def get_users(self, name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None) -> Sequence[Users]:
        stmt = select(Users)

        if name:
            stmt = stmt.where(Users.name.ilike(f"%{name}%"))
        if email:
            stmt = stmt.where(Users.email.ilike(f"%{email}%"))
        if role:
            stmt = stmt.where(Users.role == role)

        result = await self.db.execute(stmt)
        return result.scalars().all()
    

    async def get_user_by_id(self, id: int) -> Optional[Users]:
        result = await self.db.execute(
            select(Users).where(Users.id == id)
        )
        return result.scalars().first()

    async def delete_user(self, id: int) -> bool:
        user_to_delete = await self.db.get(Users, id)
        if not user_to_delete:
            return False

        await self.db.delete(user_to_delete)
        await self.db.commit()
        return True
        

    async def login_user(self, email: str, password: str) -> Optional[Users]:
        result = await self.db.execute(
            select(Users).where(Users.email == email)
        )
        user = result.scalars().first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
        