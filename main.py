from fastapi import FastAPI
from db.db_controller_user import db_get_user_by_id, db_get_users, db_add_user, db_add_user, db_delete_user, db_delete_user
from api.api_objects import UserCreate


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
    result = await db_delete_user(email, password)
    if not result:
        return {"message": "Invalid credentials", "user": None}
    
    return {"message": "Login successful", "user": result}

