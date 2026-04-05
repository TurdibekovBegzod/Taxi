import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from datetime import datetime
class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text and not message.contact:
            await message.answer("📞 Telefon raqamingizni kiriting\nNamuna: +998901234567 yoki 901234567")
            return False

        phone = message.contact.phone_number if message.contact else message.text.strip()
        digits = re.sub(r"\D", "", phone)

        if len(digits) == 9  or (len(digits) == 12 and digits.startswith("998")):
            return True
        
        await message.answer("❌ Telefon noto'g'ri\nNamuna: +998901234567 yoki 901234567")
        return False

class PeopleCountFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        text = (message.text or "").strip()
        
        if not text or not text.isdigit():
            await message.answer("❌ Faqat raqam kiriting\n👥 Masalan: 4")
            return False
        
        if 1 <= int(text) <= 10:
            return True
        
        await message.answer("❌ Odamlar soni 1-10 oralig'ida bo'lishi kerak")
        return False