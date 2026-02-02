# Here you need to cerate you keyboards

from aiogram.types import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

show_role_buttons = ReplyKeyboardMarkup(
    keyboard=[
        KeyboardButton(text = "Passenger"),
        KeyboardButton(text = 'Driver')
    ]
    ,
    resize_keyboard=True
)