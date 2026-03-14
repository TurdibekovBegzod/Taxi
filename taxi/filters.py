from aiogram import types
from aiogram.filters import BaseFilter
import re


class PhoneFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        # accept contact messages too
        if message.contact and message.contact.phone_number:
            phone = str(message.contact.phone_number)
        else:
            phone = (message.text or "").strip()

        if not phone:
            await message.answer("Telefon raqamingizni yuboring yoki yozing, iltimos.", reply_markup=None)
            return False

        digits = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"(?:998|0)?\d{9}", digits):
            await message.answer(
                "Telefon raqami noto'g'ri format. Iltimos: +998901234567 yoki 0901234567 kabi yuboring.",
                reply_markup=None
            )
            return False

        return True


class CarNumberFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        value = (message.text or "").strip().upper()

        if not value:
            await message.answer("Mashina raqamini kiriting, iltimos.", reply_markup=None)
            return False

        # O'zbek salon raqami formatlari:
        # 41A111AA (2 raqam + 1 harf + 3 raqam + 2 harf)
        # 01A1234  (2 raqam + 1 harf + 4 raqam)
        if not re.fullmatch(r"\d{2}[A-Z]\d{4}|\d{2}[A-Z]\d{3}[A-Z]{2}", value):
            await message.answer(
                "Mashina raqami noto'g'ri. Iltimos 41A111AA yoki 01A1234 formatida kiriting.",
                reply_markup=None
            )
            return False

        return True

