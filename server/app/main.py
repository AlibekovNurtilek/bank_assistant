from fastapi import FastAPI
from app.api.routers import user
app = FastAPI(title="Bank Assistant API")

@app.get("/")
async def root():
    return {"message" : "welcome"}
app.include_router(user.router)

