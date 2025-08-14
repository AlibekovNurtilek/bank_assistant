from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models import Customer
from app.db.repositories.customers import CustomerRepository
from app.services.security import hash_password, verify_password

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CustomerRepository(session)

    async def register_customer(self, *, first_name: str, last_name: str,
                                email: str, password: str, phone_number: str | None = None) -> Customer:
        existing = await self.repo.get_by_email(email.lower())
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        customer = Customer(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            middle_name=None,
            birth_date=datetime.utcnow().date(),   # демо: можно убрать/передать отдельно
            passport_number=f"DEMO-{datetime.utcnow().timestamp()}",  # демо-заглушка, замени на реальное поле
            phone_number=phone_number or "",
            email=email.lower(),
            address="",
            password_hash=hash_password(password),
        )
        await self.repo.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer

    async def validate_login(self, *, email: str, password: str) -> Customer:
        user = await self.repo.get_by_email(email.lower())
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        return user
