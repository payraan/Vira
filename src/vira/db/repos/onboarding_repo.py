from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vira.db.models.onboarding import OnboardingSession


class OnboardingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id):
        res = await self.session.execute(
            select(OnboardingSession).where(OnboardingSession.user_id == user_id)
        )
        return res.scalar_one_or_none()

    async def get_or_create(self, user_id) -> OnboardingSession:
        s = await self.get(user_id)
        if s:
            return s
        s = OnboardingSession(user_id=user_id)
        self.session.add(s)
        await self.session.commit()
        await self.session.refresh(s)
        return s

    async def set_state(self, user_id, state: str) -> OnboardingSession:
        s = await self.get_or_create(user_id)
        s.state = state
        await self.session.commit()
        await self.session.refresh(s)
        return s

    async def set_data(self, user_id, data: dict) -> OnboardingSession:
        s = await self.get_or_create(user_id)
        s.data = data
        await self.session.commit()
        await self.session.refresh(s)
        return s
