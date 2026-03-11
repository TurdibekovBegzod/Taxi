from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from .functions import (
                        language_command,
                        passenger_start,
                        travel_start, 
                        process_firstname, 
                        process_lastname, 
                        process_phone, 
                        process_location, 
                        process_time, 
                        process_people,
                        confirm_send,
                        cancel_order,
                        edit_order,
                        choose_edit_field,
                        save_edited_value

)

from .callback import (
                        language_callback,
                        process_place1,
                        process_place2
                        ) 

from aiogram.filters import CommandStart, Command
from .states import user_states
from taxi.states import taxi_states
from aiogram.filters import StateFilter


router = Router()
@router.message(F.text == "✅ Yuborish")
async def confirm_handler(message: Message, state: FSMContext, bot: Bot):
    await confirm_send(message, state, bot)

# Here you can connect your functions



# example to connect functions
# router.message.register(function_name, filters, commands)
router.message.register(language_command, Command("language"))
router.callback_query.register(language_callback, F.data.in_(["lang_uz", "lang_ru"]))
router.message.register(passenger_start, F.text.in_(["Yo'lovchi", "Passenger"]))
router.message.register(travel_start, F.text.in_(["Sayohat", "Поездка"]),StateFilter(user_states.choose_option))
router.message.register(process_firstname, StateFilter(user_states.user_firstname))
router.message.register(process_lastname, user_states.user_lastname)
router.message.register(process_phone,user_states.user_phone)
router.callback_query.register(process_place1, lambda c: c.data.startswith("place1_"), 
    StateFilter(user_states.user_place1)) 
router.callback_query.register(process_place2, lambda c: c.data.startswith("place2_"), 
    StateFilter(user_states.user_place2))
router.message.register(process_location, user_states.user_confirm)
router.message.register(process_location, StateFilter(user_states.user_location))
router.message.register(process_time, user_states.user_time)
router.message.register(process_people, user_states.user_people)
router.message.register(confirm_send, StateFilter(user_states.confirm_order), F.text == "✅ Yuborish")
router.message.register(edit_order,StateFilter(user_states.confirm_order),F.text=="✏️ Tahrirlash")
router.message.register(cancel_order,StateFilter(user_states.confirm_order),F.text=="❌ Bekor qilish")
router.message.register(choose_edit_field,StateFilter(user_states.edit_field))
router.message.register(save_edited_value,StateFilter(user_states.edit_value))