# Here you need to cerate you keyboards
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
            ]
        ]
    )


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from user.i18n import t

def passenger_keyboard(user_lang: str):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(user_lang, "passenger.travel")),
                KeyboardButton(text=t(user_lang, "passenger.my_requests")),
                KeyboardButton(text=t(user_lang, "passenger.complaints")),
                KeyboardButton(text=t(user_lang, "back"))
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def place_keyboard(user_lang: str, type: str = "from"):
    """
    type = "from" -> Qayerdan tugmalari
    type = "to"   -> Qayerga tugmalari
    """
    prefix = "place1" if type == "from" else "place2"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Toshkent", callback_data=f"{prefix}_Toshkent"),
            InlineKeyboardButton(text="Xorazm", callback_data=f"{prefix}_Xorazm")
        ]
    ])
