from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

Language = Literal["fa", "en"]

class ActivationProfile(BaseModel):
    language: Language
    niche: str
    goal: str

class ContentIdea(BaseModel):
    title: str
    hook: str
    angle: str

class WeeklyPlan(BaseModel):
    ideas: List[ContentIdea]

class DailyScript(BaseModel):
    duration_sec: int = Field(ge=15, le=90)
    script: str

class Strategy(BaseModel):
    summary: str
    tone: str
    format: str  # faceless / talking-head / mixed
    cadence: str # مثلا: روزانه / هفته‌ای 3 تا
