from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.phone import normalize_phone_number
from services.users import UserService
from user.i18n import t


async def get_lang(message: Message) -> str:
    return await UserService.get_user_language(str(message.from_user.id))


def back_texts() -> set[str]:
    return {t(lang, "button.back") for lang in ("uz", "ru", "en")}


class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        lang = await get_lang(message)

        if message.text in back_texts():
            return False

        if not message.text and not message.contact:
            await message.answer(
                f"{t(lang, 'taxi.input.phone')}\n{t(lang, 'edit.example')}: +998901234567"
            )
            return False

        phone = message.contact.phone_number if message.contact else message.text.strip()

        if normalize_phone_number(phone):
            return True

        await message.answer(t(lang, "error.phone_invalid"))
        return False


def format_phone_number(phone: str) -> str:
    """Telefon raqamni +998951197705 yoki 951197705 formatida kiriting."""
    return normalize_phone_number(phone) or phone


def format_car_number(car_number: str) -> str:
    """Mashina raqamni formatlash."""
    car_number = car_number.strip().upper()
    car_number = car_number.replace(" ", "").replace("-", "")
    return car_number
