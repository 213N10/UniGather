from fastapi import FastAPI



app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}



@app.get("/users")
async def get_users():
    return {"users": ["user1", "user2", "user3"]}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user": f"user{user_id}"}

@app.post("/users")
async def create_user(user: dict):
    return {"message": "User created", "user": user}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: dict):
    return {"message": "User updated", "user_id": user_id, "user": user}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"message": "User deleted", "user_id": user_id}

