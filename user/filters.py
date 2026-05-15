from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.phone import is_valid_phone_number
from services.users import UserService
from user.i18n import t


async def get_lang(message: Message) -> str:
    return await UserService.get_user_language(str(message.from_user.id))


def cancel_texts() -> set[str]:
    return {t(lang, "button.cancel") for lang in ("uz", "ru", "en")}


class PhoneFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        lang = await get_lang(message)

        if message.text in cancel_texts():
            return False

        if not message.text and not message.contact:
            await message.answer(
                f"{t(lang, 'input.phone')}\n{t(lang, 'edit.example')}: +998901234567"
            )
            return False

        phone = message.contact.phone_number if message.contact else message.text.strip()

        if is_valid_phone_number(phone):
            return True

        await message.answer(t(lang, "error.phone_invalid"))
        return False


class LocationFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        lang = await get_lang(message)

        if message.text in cancel_texts():
            return False

        if message.location:
            return True

        await message.answer(t(lang, "error.location_required"))
        return False


class PeopleCountFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        lang = await get_lang(message)
        text = (message.text or "").strip()

        if text in cancel_texts():
            return False

        if not text or not text.isdigit():
            await message.answer(t(lang, "error.number_required"))
            return False

        if 1 <= int(text) <= 20:
            return True

        await message.answer(t(lang, "error.people_range"))
        return False
