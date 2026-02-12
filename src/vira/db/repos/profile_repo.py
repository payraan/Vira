from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vira.db.models.profile import UserProfile


class ProfileRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id):
        res = await self.session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return res.scalar_one_or_none()

    async def upsert(self, user_id, data: dict) -> UserProfile:
        p = await self.get(user_id)
        if p is None:
            p = UserProfile(user_id=user_id, data=data)
            self.session.add(p)
        else:
            p.data = data
        await self.session.commit()
        await self.session.refresh(p)
        return p

    async def mark_completed(self, user_id) -> UserProfile:
        p = await self.get(user_id)
        if p is None:
            p = UserProfile(user_id=user_id, data={})
            self.session.add(p)
        if p.completed_at is None:
            p.completed_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(p)
        return p
