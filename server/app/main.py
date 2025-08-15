from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.settings import settings
from app.api.routers import auth as auth_router, chat as chat_router
from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.INFO,  # чтобы INFO был виден
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


app = FastAPI(title="Bank Assistant API")

# ✅ Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://frontend-domain.com"],  # адреса фронта
    allow_credentials=True,  # важно для сессионных cookies
    allow_methods=["*"],     # или конкретные методы: ["GET", "POST"]
    allow_headers=["*"],     # или ["Content-Type", "Authorization"]
)

# ✅ Сессии
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="session",
    same_site="lax",
    https_only=False if settings.debug else True
)

app.include_router(auth_router.router)
app.include_router(chat_router.router)

@app.get("/")
async def root():
    return {"message": "welcome"}

