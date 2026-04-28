import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if not message.text and not message.contact:
            await message.answer("📞 Telefon raqamingizni kiriting\nNamuna: +998776543423 yoki 998765434")
            return False

        phone = message.contact.phone_number if message.contact else message.text.strip()

        if re.fullmatch(r"(\+998\d{9}|\d{9})", phone):
            return True
        
        await message.answer("❌ Telefon noto'g'ri\nNamuna: +998776543423 yoki 998765434")
        return False
    
class PeopleCountFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        text = (message.text or "").strip()
        
        if not text or not text.isdigit():
            await message.answer("❌ Faqat raqam kiriting\n👥 Masalan: 4")
            return False
        
        if 1 <= int(text) <= 20:
            return True
        
        await message.answer("Aniq ketadigan odamlarning sonini kriting ")
        return False
    

    