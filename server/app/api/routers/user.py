from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_session
from app.db.repositories import UserRepository
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    # В бою тут должен быть хэш пароля
    user = await repo.create(username=data.username, email=data.email, password_hash=data.password)
    return user

@router.get("", response_model=list[UserOut])
async def list_users(session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    users = await repo.list(limit=100)
    return users
