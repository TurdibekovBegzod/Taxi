# Here you need write your functions
from aiogram.types import Message
from aiogram import Bot
from user.keyboards import show_role_buttons

async def start_command(message : Message, bot : Bot):
    await message.answer(text = "Choose your role!", reply_markup=show_role_buttons)