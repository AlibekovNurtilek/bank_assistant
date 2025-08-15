from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_session
from typing import Optional
from app.db.repositories.customers import CustomerRepository

SESSION_KEY = "user_id"

async def get_db_session():
    async for s in get_session():
        yield s

async def get_current_customer(request: Request, session: AsyncSession = Depends(get_db_session)):
    print("SESSION DATA:", dict(request.session))
    uid = request.session.get(SESSION_KEY)
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user = await CustomerRepository(session).get_by_id(int(uid))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_optional_customer(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    uid = request.session.get(SESSION_KEY)
    if not uid:
        return None
    user = await CustomerRepository(session).get_by_id(int(uid))
    return user 