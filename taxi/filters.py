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


class CarNumberFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            await message.answer("🚗 Mashina raqamini kiriting!\nMisol: 01A123AA")
            return False
        
        car_number = message.text.strip().upper()
        car_number = car_number.replace(' ', '').replace('-', '')
        
        # Harflar va raqamlardan iboratligini tekshirish
        if not re.match(r'^[A-Z0-9]+$', car_number):
            await message.answer(
                "❌ Mashina raqami faqat harf va raqamlardan iborat bo'lishi kerak!\n"
                "Misol: 01A123AA"
            )
            return False
        
        # Barcha mumkin bo'lgan patternlar
        patterns = [
            # Eski format: 2 raqam + 1 harf + 3-4 raqam + 0-2 harf
            r'^\d{2}[A-Z]\d{3,4}[A-Z]{0,2}$',
            # Yangi format: 1 raqam + 1 harf + 3-4 raqam + 0-2 harf
            r'^\d[A-Z]\d{3,4}[A-Z]{0,2}$',
            # Toshkent: 2 raqam + 2 harf + 3-4 raqam
            r'^\d{2}[A-Z]\d{3}(CD|TD)$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, car_number):
                return True
        
        await message.answer(
            "❌ Mashina raqami noto'g'ri formatda!\n\n"
            "✅ Qabul qilinadigan formatlar:\n"
            "📝 Misol: \n 01A123AA yoki 1A1234A"
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