# Here you need to cerate you keyboards

from aiogram.types import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton


show_role_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = 'Driver'), KeyboardButton(text = "Passenger")]
    ]
    ,
    resize_keyboard=True
)
sign_up = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Sign up")
        ]
    ],
    resize_keyboard=True
)
get_contact = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Get contact", request_contact=True)
        ]
    ],
    resize_keyboard=True
)
confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Confirm")
        ]
    ]
    ,resize_keyboard=True
)
taxi_profile = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Info"), KeyboardButton(text = "Suggestions and comp/s")
        ]
    ],
    resize_keyboard=True
)