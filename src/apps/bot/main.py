from __future__ import annotations

import asyncio

import structlog
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from vira.settings import settings
from infra.logging.logger import setup_logging
from infra.db.database import get_sessionmaker
from vira.db.repos.user_repo import UserRepo
from vira.db.repos.onboarding_repo import OnboardingRepo
from vira.db.repos.profile_repo import ProfileRepo
from vira.ai.engine import AIEngine


setup_logging()
log = structlog.get_logger()

router = Router()


def kb(*rows: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=True,
        one_time_keyboard=True,
    )



@router.message(Command("restart"))

@router.message(Command("plan"))
async def plan_handler(message: Message):
    tg_id = str(message.from_user.id) if message.from_user else ""
    if not tg_id:
        return

    async_session = get_sessionmaker()
    async with async_session() as session:
        user_repo = UserRepo(session)
        u = await user_repo.get_or_create(tg_id)

        profile_repo = ProfileRepo(session)
        prof = await profile_repo.get(u.id)

        if not prof or not prof.data:
            await message.answer("اول پروفایل رو کامل کن 👇\n/start")
            return

        engine = AIEngine()
        out = await engine.generate_all(prof.data)

    st = out["strategy"]
    ideas = out["weekly_plan"]["ideas"]
    followups = out.get("followup_questions", [])

    lines = []
    lines.append("✅ پلن اولیه Vira آماده شد")
    lines.append("")
    lines.append(f"**استراتژی:** {st['summary']}")
    lines.append(f"**لحن:** {st['tone']} | **فرمت:** {st['format']} | **ریتم:** {st['cadence']}")
    lines.append("")
    lines.append("🔥 ایده‌های این هفته:")
    for i, it in enumerate(ideas, 1):
        lines.append(f"{i}) {it['title']} — هوک: {it['hook']} ({it['angle']})")
    lines.append("")
    lines.append("🧪 نمونه اسکریپت:")
    lines.append(out["sample_script"]["script"])
    if followups:
        lines.append("")
        lines.append("برای دقیق‌تر شدن، جواب بده:")
        for q in followups[:3]:
            lines.append(f"• {q}")

    await message.answer("\n".join(lines))
async def restart_handler(message: Message):
    tg_id = str(message.from_user.id) if message.from_user else ""
    async_session = get_sessionmaker()

    async with async_session() as session:
        user_repo = UserRepo(session)
        u = await user_repo.get_or_create(tg_id)

        onboarding_repo = OnboardingRepo(session)
        profile_repo = ProfileRepo(session)

        await onboarding_repo.delete(u.id)
        await profile_repo.delete(u.id)

    await message.answer("ریست شد ✅ حالا از اول شروع می‌کنیم.", reply_markup=ReplyKeyboardRemove())
    # trigger start flow
    await start_handler(message)

@router.message(CommandStart())
async def start_handler(message: Message):
    tg_id = str(message.from_user.id) if message.from_user else ""
    async_session = get_sessionmaker()

    async with async_session() as session:
        user_repo = UserRepo(session)
        u = await user_repo.get_or_create(tg_id)

        onboarding_repo = OnboardingRepo(session)
        ob = await onboarding_repo.get_or_create(u.id)

        profile_repo = ProfileRepo(session)
        prof = await profile_repo.get(u.id)

    if prof and prof.completed_at:
        await message.answer("پروفایل تو قبلاً کامل شده ✅\nاگر خواستی دوباره از نو بسازی، بگو: /restart")
        return

    if ob.state == "Q1_LANGUAGE":
        await message.answer("بریم شروع کنیم 👇\nزبان محتوایی که می‌خوای تولید کنی چیه؟",
            reply_markup=kb(["فارسی", "انگلیسی"])
        )
        return

    await message.answer("ادامه‌ی آنبوردینگ رو بگو /start بزن تا از همونجا ادامه بدیم.")


async def main():
    log.info("bot_starting")

    if not settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is empty. Put it in .env")
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    log.info("bot_polling_started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

@router.message()
async def onboarding_answers(message: Message):
    tg_id = str(message.from_user.id) if message.from_user else ""
    text = (message.text or "").strip()
    if not tg_id or not text:
        return

    async_session = get_sessionmaker()
    async with async_session() as session:
        user_repo = UserRepo(session)
        u = await user_repo.get_or_create(tg_id)

        onboarding_repo = OnboardingRepo(session)
        ob = await onboarding_repo.get_or_create(u.id)

        profile_repo = ProfileRepo(session)
        prof = await profile_repo.get(u.id)

        # if completed, ignore
        if prof and prof.completed_at:
            await message.answer("پروفایل تو قبلاً کامل شده ✅")
            return

        data = dict(ob.data or {})

        if ob.state == "Q1_LANGUAGE":
            if text not in {"فارسی", "انگلیسی"}:
                await message.answer("یکی از گزینه‌ها رو بزن 👇", reply_markup=kb(["فارسی", "انگلیسی"]))
                return
            data["language"] = "fa" if text == "فارسی" else "en"
            await onboarding_repo.set_data(u.id, data)
            await onboarding_repo.set_state(u.id, "Q2_NICHE")
            await message.answer(
                "حوزه‌ی اصلی محتوات چیه؟",
                reply_markup=kb(["AI/تکنولوژی", "مالی/کریپتو", "آموزشی", "سرگرمی", "لایف‌استایل"], ["سایر"])
            )
            return

        if ob.state == "Q2_NICHE":
            data["niche"] = text
            await onboarding_repo.set_data(u.id, data)
            await onboarding_repo.set_state(u.id, "Q3_GOAL")
            await message.answer(
                "هدف اصلی تو چیه؟",
                reply_markup=kb(["درآمد دلاری", "رشد مخاطب فارسی", "برند شخصی", "فروش محصول/سرویس"])
            )
            return

        if ob.state == "Q3_GOAL":
            data["goal"] = text
            await onboarding_repo.set_data(u.id, data)

            # profile upsert + mark completed
            await profile_repo.upsert(u.id, data)
            await profile_repo.mark_completed(u.id)
            await onboarding_repo.set_state(u.id, "DONE")

            await message.answer(
                "عالی ✅ پروفایلت کامل شد.\nحالا می‌تونم برات پلن محتوا و ایده‌ها رو بسازم.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

        await message.answer("برای شروع دوباره: /start")
