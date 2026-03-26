import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from datetime import datetime
# Telefon raqam filteri
class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text and not message.contact:
            await message.answer("📞 Telefon raqamingizni kiriting\nNamuna: +998901234567 yoki 901234567")
            return False

        phone = message.contact.phone_number if message.contact else message.text.strip()
        digits = re.sub(r"\D", "", phone)

        if len(digits) == 9  or (len(digits) == 12 and digits.startswith("998")):
            return True
        
        await message.answer("❌ Telefon noto'g'ri\n📞 Namuna: +998901234567 yoki 901234567")
        return False
# Sana va vaqt filteri
class DateTimeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        text = (message.text or "").strip()
        
        if not text:
            await message.answer("📅 Sana va vaqtni kiriting\nNamuna: 25.03.2026 14:30")
            return False

        formats = ["%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"]
        
        for fmt in formats:
            try:
                datetime.strptime(text, fmt)
                return True
            except:
                continue
        
        await message.answer("❌ Sana va vaqt noto'g'ri\n📅 Namuna: 25.03.2026 14:30")
        return False


# Odamlar soni filteri
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