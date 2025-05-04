from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from api.api_objects import UserCreate, UserUpdate, AdminUserUpdate
from db.db_models import Users
from api.user_auth import hash_password, verify_password

ENGINE = create_async_engine("postgresql+asyncpg://postgres:1101@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_user(user: UserCreate):
    async with SESSION() as session:
        async with session.begin():
            new_user = Users(
                name=user.name,
                email=user.email,
                password_hash= hash_password(user.password),
                role=user.role
            )
            user_exists = await session.execute(
                select(Users).where(Users.email == user.email)
            )
            if user_exists.scalars().first():
                return None
            session.add(new_user)
            await session.commit()
            return new_user.id 
        
async def db_update_user(user: UserUpdate, id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            user_to_update = await session.get(Users, id)
            if user_to_update:
                if user.name:
                    user_to_update.name = user.name
                if user.email:
                    user_to_update.email = user.email
                if user.password:
                    user_to_update.password_hash = hash_password(user.password)
               
                await session.commit()
                return True
            return False
        

async def db_get_users(name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None) -> List[Users]:
    async with SESSION() as session:
        stmt = select(Users)

        if name:
            stmt = stmt.where(Users.name.ilike(f"%{name}%"))
        if email:
            stmt = stmt.where(Users.email.ilike(f"%{email}%"))
        if role:
            stmt = stmt.where(Users.role == role)

        result = await session.execute(stmt)
        return result.scalars().all()
    

async def db_get_user_by_id(id: int) -> Optional[Users]:
    async with SESSION() as session:
        stmt = select(Users).where(Users.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()
    

async def db_delete_user(id: int) -> bool:
    async with SESSION() as session:
        async with session.begin():
            user_to_delete = await session.get(Users, id)
            if user_to_delete:
                await session.delete(user_to_delete)
                await session.commit()
                return True
            return False
        

async def db_login_user(email: str, password: str) -> Optional[Users]:
    async with SESSION() as session:
        stmt = select(Users).where(Users.email == email)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
        