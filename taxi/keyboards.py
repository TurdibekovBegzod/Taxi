# Here you need to cerate you keyboards

from aiogram.types import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton


show_role_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = '🚖 Haydovchi'), KeyboardButton(text = "👤 Yo'lovchi")]
    ]
    ,
    resize_keyboard=True
)
sign_up = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Ro‘yxatdan o‘tish")
        ]
    ],
    resize_keyboard=True
)
get_contact = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "📱 Telefon raqamini yuborish", request_contact=True)
        ]
    ],
    resize_keyboard=True
)
confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Tasdiqlash")
        ]
    ]
    ,resize_keyboard=True
)
taxi_profile = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "📄 Ma'lumot"), KeyboardButton(text = "📝 Ma'lumotlarni o'zgartirish")
        ],
        [
            KeyboardButton(text = "📢 Kanalga o'tish")
        ],
        [
            KeyboardButton(text = "Shikoyatlar va takliflar")
        ]
    ],
    resize_keyboard=True
)

edit_profile = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = "Ism"), KeyboardButton(text = "Familiya")],
        [KeyboardButton(text = "Telefon"), KeyboardButton(text = "Mashina modeli")],
        [KeyboardButton(text = "Mashina raqami")],
        [KeyboardButton(text = "◀️ Orqaga")]
    ],
    resize_keyboard=True
)
btn_back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="◀️ Orqaga")]
    ],
    resize_keyboard=True
)