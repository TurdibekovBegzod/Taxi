# Here you need to cerate you keyboards
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from user.i18n import t
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




def passenger_keyboard(user_lang: str):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(user_lang, "passenger.travel"))
            ],
            [
                KeyboardButton(text="📢 Kanalga o'tish")
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
        ],
        [
            InlineKeyboardButton(text="Samarqand", callback_data=f"{prefix}_Samarqand"),
            InlineKeyboardButton(text="Buxoro", callback_data=f"{prefix}_Buxoro")
        ],
        [
            InlineKeyboardButton(text="Farg'ona", callback_data=f"{prefix}_Farg'ona"),
            InlineKeyboardButton(text="Andijon", callback_data=f"{prefix}_Andijon")
        ],
        [
            InlineKeyboardButton(text="Namangan", callback_data=f"{prefix}_Namangan"),
            InlineKeyboardButton(text="Qashqadaryo", callback_data=f"{prefix}_Qashqadaryo")
        ],
        [
            InlineKeyboardButton(text="Navoiy", callback_data=f"{prefix}_Navoiy"),
            InlineKeyboardButton(text="Surxondaryo", callback_data=f"{prefix}_Surxondaryo")
        ],
        [
            InlineKeyboardButton(text="Jizzax", callback_data=f"{prefix}_Jizzax"),
            InlineKeyboardButton(text="Sirdaryo", callback_data=f"{prefix}_Sirdaryo")
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
            [KeyboardButton(text="Telefon"),KeyboardButton(text="Odamlar soni")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )




def receive(order_id, user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Qabul qilish",
                    callback_data=f"accept_{order_id}|uid_{user_id}"
                )
            ]
        ]
    )

btn_location_keyboard =  ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
        ],
        resize_keyboard=True
    )
btn_phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamini yuborish", request_contact=True)]
        ],
        resize_keyboard=True
    )