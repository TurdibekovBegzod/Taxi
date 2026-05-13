from aiogram.filters import BaseFilter
from aiogram.types import Message
from services.phone import normalize_phone_number

class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text and not message.contact:
            await message.answer("📞 Telefon raqamingizni kiriting\nNamuna: +998901234567 yoki 901234567")
            return False

        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()
        
        if normalize_phone_number(phone):
            return True
        
        await message.answer(
            "❌ Telefon raqam noto'g'ri formatda!\n\n"
            "✅ Qabul qilinadigan formatlar:\n"
            "• +998901234567\n"
            "• 901234567\n"
            
        )
        return False




def format_phone_number(phone: str) -> str:
    """Telefon raqamni +998951197705 yoki 951197705 formatida kriting"""
    return normalize_phone_number(phone) or phone

def format_car_number(car_number: str) -> str:
    """Mashina raqamni formatlash"""
    car_number = car_number.strip().upper()
    car_number = car_number.replace(' ', '').replace('-', '')
    return car_number
