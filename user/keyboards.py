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
                KeyboardButton(text=t(user_lang, "passenger.travel"))
            ],
            [
                KeyboardButton(text="Channel")
            ],
            [
                KeyboardButton(text=t(user_lang, "passenger.complaints"))
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

# ==================================================
# ==========================================================
# CONFIRM KEYBOARD
def confirm_keyboard(user_lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yuborish")],
            [KeyboardButton(text="✏️ Tahrirlash")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

# ====================
def edit_keyboard(user_lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ism"), KeyboardButton(text="Familiya")],
            [KeyboardButton(text="Qayerdan"), KeyboardButton(text="Qayerga")],
            [KeyboardButton(text="Lokatsiya")],
            [KeyboardButton(text="Sana va vaqt"),KeyboardButton(text="Telefon")],
            [KeyboardButton(text="Odamlar soni")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )


