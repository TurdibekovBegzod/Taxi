from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from user.i18n import t


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ],
        ]
    )


def passenger_keyboard(user_lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "passenger.travel"))],
            [KeyboardButton(text=t(user_lang, "passenger.channel"))],
            [KeyboardButton(text=t(user_lang, "passenger.complaints"))],
        ],
        resize_keyboard=True
    )


def place_keyboard(user_lang: str, type: str = "from", back: bool = False):
    prefix = "place1" if type == "from" else "place2"
    keyboard = [
        [
            InlineKeyboardButton(text="Toshkent", callback_data=f"{prefix}_Toshkent"),
            InlineKeyboardButton(text="Xorazm", callback_data=f"{prefix}_Xorazm"),
        ],
        [
            InlineKeyboardButton(text="Samarqand", callback_data=f"{prefix}_Samarqand"),
            InlineKeyboardButton(text="Buxoro", callback_data=f"{prefix}_Buxoro"),
        ],
        [
            InlineKeyboardButton(text="Farg'ona", callback_data=f"{prefix}_Farg'ona"),
            InlineKeyboardButton(text="Andijon", callback_data=f"{prefix}_Andijon"),
        ],
        [
            InlineKeyboardButton(text="Namangan", callback_data=f"{prefix}_Namangan"),
            InlineKeyboardButton(text="Qashqadaryo", callback_data=f"{prefix}_Qashqadaryo"),
        ],
        [
            InlineKeyboardButton(text="Navoiy", callback_data=f"{prefix}_Navoiy"),
            InlineKeyboardButton(text="Surxondaryo", callback_data=f"{prefix}_Surxondaryo"),
        ],
        [
            InlineKeyboardButton(text="Jizzax", callback_data=f"{prefix}_Jizzax"),
            InlineKeyboardButton(text="Sirdaryo", callback_data=f"{prefix}_Sirdaryo"),
        ],
        [
            InlineKeyboardButton(text="Qoraqalpog'iston", callback_data=f"{prefix}_Qoraqalpog'iston")
        ],
    ]

    if back:
        keyboard.append([
            InlineKeyboardButton(text=t(user_lang, "button.back"), callback_data="place_back")
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_keyboard(user_lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "button.send"))],
            [KeyboardButton(text=t(user_lang, "button.edit"))],
            [KeyboardButton(text=t(user_lang, "button.cancel"))],
        ],
        resize_keyboard=True
    )


def edit_keyboard(user_lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "field.firstname")), KeyboardButton(text=t(user_lang, "field.lastname"))],
            [KeyboardButton(text=t(user_lang, "field.from")), KeyboardButton(text=t(user_lang, "field.to"))],
            [KeyboardButton(text=t(user_lang, "field.location"))],
            [KeyboardButton(text=t(user_lang, "field.phone")), KeyboardButton(text=t(user_lang, "field.people"))],
            [KeyboardButton(text=t(user_lang, "button.back"))],
        ],
        resize_keyboard=True
    )


def receive(order_id, user_id, user_lang: str = "uz"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(user_lang, "order.accept_button"),
                    callback_data=f"accept_{order_id}|uid_{user_id}"
                )
            ]
        ]
    )


def location_keyboard(user_lang: str = "uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "button.send_location"), request_location=True)],
            [KeyboardButton(text=t(user_lang, "button.cancel"))],
        ],
        resize_keyboard=True
    )


def phone_keyboard(user_lang: str = "uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "button.send_phone"), request_contact=True)],
            [KeyboardButton(text=t(user_lang, "button.cancel"))],
        ],
        resize_keyboard=True
    )


def back_keyboard(user_lang: str = "uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "button.back"))]
        ],
        resize_keyboard=True
    )


def cancel_keyboard_for(user_lang: str = "uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(user_lang, "button.cancel"))]
        ],
        resize_keyboard=True
    )


btn_location_keyboard = location_keyboard("uz")
btn_phone_keyboard = phone_keyboard("uz")
btn_back = back_keyboard("uz")
cancel_keyboard = cancel_keyboard_for("uz")
