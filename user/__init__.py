from aiogram import Router, F
from .functions import start_command
from aiogram.filters import CommandStart
router = Router()

# Here you can connect your functions


router.message.register(start_command, CommandStart)

# example to connect functions
# router.message.register(function_name, filters, commands)
