from __future__ import annotations

from vira.ai.providers.base import AIProvider
from vira.ai.schemas import ActivationProfile, WeeklyPlan, ContentIdea, DailyScript, Strategy

class DummyProvider(AIProvider):
    async def build_strategy(self, profile: ActivationProfile) -> Strategy:
        return Strategy(
            summary=f"استراتژی پایه برای {profile.niche} با هدف {profile.goal}",
            tone="شفاف و آموزشی",
            format="faceless",
            cadence="هفته‌ای 5 شورت"
        )

    async def build_weekly_plan(self, profile: ActivationProfile) -> WeeklyPlan:
        ideas = [
            ContentIdea(title=f"۳ اشتباه رایج در {profile.niche}", hook="۹۰٪ اینو اشتباه می‌رن!", angle="آموزشی"),
            ContentIdea(title=f"خبر داغ امروز {profile.niche}", hook="همین الان دیدیش؟", angle="واکنشی"),
            ContentIdea(title=f"راهنمای سریع {profile.niche}", hook="۶۰ ثانیه طلا!", angle="چک‌لیست"),
        ]
        return WeeklyPlan(ideas=ideas)

    async def build_daily_script(self, profile: ActivationProfile, idea_title: str) -> DailyScript:
        return DailyScript(
            duration_sec=45,
            script=f"هوک قوی درباره {idea_title}…\nبدنه کوتاه آموزشی…\nCTA ملایم."
        )
