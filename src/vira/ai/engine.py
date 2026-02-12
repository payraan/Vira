from __future__ import annotations

from vira.ai.schemas import ActivationProfile
from vira.ai.providers.dummy import DummyProvider

class AIEngine:
    def __init__(self):
        self.provider = DummyProvider()

    async def generate_all(self, profile_data: dict):
        profile = ActivationProfile(**profile_data)

        strategy = await self.provider.build_strategy(profile)
        weekly = await self.provider.build_weekly_plan(profile)
        script = await self.provider.build_daily_script(profile, weekly.ideas[0].title)

        # Progressive questions inferred (not asked yet)
        followups = []
        if profile.niche.lower().startswith("مالی"):
            followups.append("محتوا تحلیلی باشه یا خبری؟")
        if profile.goal == "رشد مخاطب فارسی":
            followups.append("ترجیح می‌دی لحن خودمونی باشه یا رسمی؟")

        return {
            "strategy": strategy.model_dump(),
            "weekly_plan": weekly.model_dump(),
            "sample_script": script.model_dump(),
            "followup_questions": followups,
        }
