from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_customer, SESSION_KEY
from app.schemas.auth import RegisterRequest, LoginRequest, CustomerOut
from app.services.auth import AuthService

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register", response_model=CustomerOut, status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db_session)):
    user = await AuthService(session).register_customer(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=payload.password,
        phone_number=payload.phone_number,
    )
    return CustomerOut.model_validate(user)

@router.post("/login")
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_db_session)):
    user = await AuthService(session).validate_login(email=payload.email, password=payload.password)
    request.session[SESSION_KEY] = user.id
    return JSONResponse({"message": "Login successful", "user_id": user.id})

@router.post("/logout")
async def logout(request: Request):
    request.session.pop(SESSION_KEY, None)
    return {"message": "Logged out successfully"}

@router.get("/user", response_model=CustomerOut)
async def get_me(current=Depends(get_current_customer)):
    return CustomerOut.model_validate(current)
