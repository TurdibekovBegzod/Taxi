from aiogram import Bot, Dispatcher
from asyncio import run
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import admin
import taxi
import user
import logging
import sys
import os
from dotenv import load_dotenv
from data import models 

log_format = "%(asctime)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPERADMIN = os.getenv("SUPERADMIN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Check .env")

if not SUPERADMIN:
    raise RuntimeError("SUPERADMIN not found. Check .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

from user.my_scheduler import scheduler


async def startup(bot: Bot):
    try:
        await bot.send_message(chat_id=int(SUPERADMIN), text="Bot ishga tushdi! ✅")
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.error(f"Startup message error: {e}")

async def shutdown(bot: Bot):
    try:
        await bot.send_message(chat_id=int(SUPERADMIN), text="Bot ishdan to'xtadi! ❌")
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.error(f"Shutdown message error: {e}")

async def main():
    scheduler.start()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    dp.include_router(admin.router)
    dp.include_router(taxi.router)
    dp.include_router(user.router)

    await bot.set_my_commands([
        BotCommand(command="/start", description="Botni ishga tushirish"),
        BotCommand(command ="/change_role", description="Foydalanuvchi darajasini o'zgartirish")
    ])

    try:
        await dp.start_polling(bot, polling_timeout=1)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    run(main())
