from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from api.api_objects import UserCreate, UserUpdate, AdminUserUpdate
from db.db_models import Users

ENGINE = create_async_engine("postgresql+asyncpg://postgres:1101@localhost:5432/uni_gather")
SESSION = async_sessionmaker(ENGINE, expire_on_commit=False)

async def db_add_user(user: UserCreate):
    async with SESSION() as session:
        async with session.begin():
            new_user = Users(
                name=user.name,
                email=user.email,
                password_hash=user.password,
                role=user.role
            )
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
                    user_to_update.password_hash = user.password
                if user.role:
                    user_to_update.role = user.role
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
        