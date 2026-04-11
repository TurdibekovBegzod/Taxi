# router.py (sizning router faylingiz)

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
                        process_people,
                        confirm_send,
                        cancel_order,
                        edit_order,
                        choose_edit_field,
                        save_edited_value,
                        channel_handler,
                        complaints_start,
                        complaints_handler,
                        back_to_choose_option
)

from .callback import (
                        language_callback,
                        process_place1,
                        process_place2,
                        accept_order,
                        contact_passenger,
                        passenger_yes,
                        passenger_no,
                        driver_yes,
                        driver_no,
                        confirm_order,
                        client_yes,
                        client_no
) 

from aiogram.filters import CommandStart, Command
from .states import user_states
from taxi.states import taxi_states
from aiogram.filters import StateFilter

from .filters import (
    PhoneFilter,
    PeopleCountFilter,
)

router = Router()

@router.message(F.text == "✅ Yuborish")
async def confirm_handler(message: Message, state: FSMContext, bot: Bot):
    await confirm_send(message, state, bot)

# ======================
# COMMAND LAR
router.message.register(language_command, Command("language"))
router.callback_query.register(language_callback, F.data.in_(["lang_uz", "lang_ru"]))
router.message.register(passenger_start, F.text.in_(["👤 Yo'lovchi", "👤 Passenger"]))
router.message.register(travel_start, F.text.in_(["🚖 E’lon yaratish", "Поездка"]))

# ======================
# ASOSIY MA'LUMOTLAR - FILTERLAR BILAN
router.message.register(process_firstname, StateFilter(user_states.user_firstname))
router.message.register(process_lastname, StateFilter(user_states.user_lastname))

# Telefon - filter bilan
router.message.register(
    process_phone,
    StateFilter(user_states.user_phone),
    PhoneFilter()
)

router.callback_query.register(process_place1, lambda c: c.data.startswith("place1_"), StateFilter(user_states.user_place1))
router.callback_query.register(process_place2, lambda c: c.data.startswith("place2_"), StateFilter(user_states.user_place2))

router.message.register(process_location, StateFilter(user_states.user_location))
router.message.register(process_location, StateFilter(user_states.user_confirm))

# Odamlar soni - filter bilan
router.message.register(
    process_people,
    StateFilter(user_states.user_people),
    PeopleCountFilter()
)

# ======================
# BUYURTMA HOLATI
router.message.register(confirm_send, StateFilter(user_states.confirm_order), F.text == "✅ Yuborish")
router.message.register(edit_order, StateFilter(user_states.confirm_order), F.text == "✏️ Tahrirlash")
router.message.register(cancel_order, StateFilter(user_states.confirm_order), F.text == "❌ Bekor qilish")
router.message.register(choose_edit_field, StateFilter(user_states.edit_field))

# TAHRIRLASH - FILTERLAR BILAN ISHLASHI UCHUN
@router.message(StateFilter(user_states.edit_value))
async def edit_value_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    editing_field = data.get("editing_field")
    
    # Qaysi maydon tahrirlanayotganiga qarab filter qo'llash
    if editing_field == "user_phone":
        phone_filter = PhoneFilter()
        if not await phone_filter(message):
            return
        await save_edited_value(message, state, bot)
    
    elif editing_field == "user_people":
        people_filter = PeopleCountFilter()
        if not await people_filter(message):
            return
        await save_edited_value(message, state, bot)
    
    else:
        await save_edited_value(message, state, bot)

# ======================
# CALLBACK QUERY LAR
router.callback_query.register(accept_order, F.data.startswith("accept_"))
# router.callback_query.register(contact_passenger, F.data.startswith("contact_"))
router.callback_query.register(passenger_yes, F.data.startswith("passenger_yes_"))
router.callback_query.register(passenger_no, F.data.startswith("passenger_no_"))
router.callback_query.register(driver_yes, F.data.startswith("driver_yes_"))
router.callback_query.register(driver_no, F.data.startswith("driver_no_"))
router.callback_query.register(confirm_order, F.data.startswith("confirm_"))
router.callback_query.register(client_yes, F.data.startswith("client_yes_"))
router.callback_query.register(client_no, F.data.startswith("client_no_"))

# ======================
# BOSHQA HANDLERLAR
router.message.register(channel_handler, F.text == "📢 Kanalga o'tish")
router.message.register(complaints_start, user_states.choose_option, lambda msg: msg.text == "Shikoyatlar va takliflar")
router.message.register(back_to_choose_option, user_states.complaint_text, F.text == "◀️ Orqaga")
router.message.register(complaints_handler, StateFilter(user_states.complaint_text))