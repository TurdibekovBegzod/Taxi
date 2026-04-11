import re
from aiogram.filters import BaseFilter
from aiogram.types import Message

class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text and not message.contact:
            await message.answer("📞 Telefon raqamingizni kiriting\nNamuna: +998901234567 yoki 901234567")
            return False

        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()
        
        digits = re.sub(r"\D", "", phone)        
        if len(digits) == 9:
            return True
        elif len(digits) == 12 and digits.startswith('998'):
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
    digits = re.sub(r"\D", "", phone.strip())
    
    if len(digits) == 9:
        digits = '998' + digits[1:]
    elif len(digits) == 12 and digits.startswith('998'):
        pass
    else:
        return phone
    
    return '+' + digits

def format_car_number(car_number: str) -> str:
    """Mashina raqamni formatlash"""
    car_number = car_number.strip().upper()
    car_number = car_number.replace(' ', '').replace('-', '')
    return car_number