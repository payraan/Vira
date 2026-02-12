from __future__ import annotations

import asyncio

import structlog
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from vira.settings import settings
from infra.logging.logger import setup_logging
from infra.db.database import get_sessionmaker
from vira.db.repos.user_repo import UserRepo


setup_logging()
log = structlog.get_logger()

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    tg_id = str(message.from_user.id) if message.from_user else ""
    async_session = get_sessionmaker()

    async with async_session() as session:
        repo = UserRepo(session)
        u = await repo.get_or_create(tg_id)

    await message.answer(f"سلام! ✅ ثبت شدی.\nuser_id: {u.id}\ntelegram_id: {u.telegram_id}")


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
