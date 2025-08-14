from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer

class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        res = await self.session.execute(select(Customer).where(Customer.id == customer_id))
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        res = await self.session.execute(select(Customer).where(Customer.email == email))
        return res.scalar_one_or_none()

    async def add(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()  # чтобы получить id без отдельного запроса
        return customer
