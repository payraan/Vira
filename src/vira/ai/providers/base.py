from __future__ import annotations
from abc import ABC, abstractmethod

from vira.ai.schemas import ActivationProfile, WeeklyPlan, DailyScript, Strategy

class AIProvider(ABC):
    @abstractmethod
    async def build_strategy(self, profile: ActivationProfile) -> Strategy: ...

    @abstractmethod
    async def build_weekly_plan(self, profile: ActivationProfile) -> WeeklyPlan: ...

    @abstractmethod
    async def build_daily_script(self, profile: ActivationProfile, idea_title: str) -> DailyScript: ...
