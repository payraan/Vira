from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vira.db.models.user import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        res = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return res.scalar_one_or_none()

    async def create(self, telegram_id: str) -> User:
        u = User(telegram_id=telegram_id)
        self.session.add(u)
        await self.session.commit()
        await self.session.refresh(u)
        return u

    async def get_or_create(self, telegram_id: str) -> User:
        u = await self.get_by_telegram_id(telegram_id)
        if u:
            return u
        return await self.create(telegram_id)
