
from data.models import Taxi
from data.crud_commands import get

async def is_driver(telegram_id: str) -> bool:
    """Foydalanuvchi haydovchi ekanligini tekshirish"""
    driver = await get(Taxi, {"telegram_id": str(telegram_id)})
    return driver is not None

async def get_driver(telegram_id: str):
    """Haydovchi ma'lumotlarini olish"""
    return await get(Taxi, {"telegram_id": str(telegram_id)})