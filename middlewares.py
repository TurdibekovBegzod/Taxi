from aiogram import BaseMiddleware
from aiogram.types import Message
from services.users import UserService
from aiogram import Dispatcher
user_service = UserService()

class LastUsedMiddleware(BaseMiddleware):
    async def __call__(self, handler, event : Message, data):
        user_telegram_id = str(event.from_user.id)
        

        user = await user_service.get_user_by_telegram_id(telegram_id=user_telegram_id)

        if not user:
            user_data = {
                "telegram_id" : user_telegram_id
            }
            await user_service.create_user(user_data=user_data)

        await user_service.update_user(telegram_id=user_telegram_id)

        return await handler(event, data)
    

def register_middleware(dispatcher : Dispatcher):
    dispatcher.message.middleware(LastUsedMiddleware())