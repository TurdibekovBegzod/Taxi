from aiogram.types import Message
from aiogram import Bot
from .keyboards import (
    show_role_buttons,
    role_keyboard,
    sign_up,
    sign_up_keyboard,
    get_contact,
    contact_keyboard,
    confirm,
    taxi_confirm_keyboard,
    taxi_profile,
    taxi_profile_keyboard,
    edit_profile,
    edit_profile_keyboard,
    btn_back,
    taxi_back_keyboard,
    btn_back_and_phone,
    taxi_back_and_phone_keyboard,
)

from aiogram.fsm.context import FSMContext
from .states import taxi_states
from user.keyboards import passenger_keyboard
from user.states import user_states
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from data import crud_commands, models
from services.phone import normalize_phone_number
from services.users import UserService
from user.i18n import t


async def start_command_answer(message: Message, bot: Bot, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await message.answer(
        text=f"{t(user_lang, 'start.welcome')}\n\n{t(user_lang, 'role.choose')}",
        reply_markup=role_keyboard(user_lang),
    )
    await state.clear()
    await state.set_state(taxi_states.choosing_role)


async def change_role_command_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    await message.answer(text=t(user_lang, "role.choose"), reply_markup=role_keyboard(user_lang))
    await state.set_state(taxi_states.choosing_role)


async def to_choose_a_role_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    driver_labels = {t(lang, "role.driver") for lang in ("uz", "ru", "en")}
    passenger_labels = {t(lang, "role.passenger") for lang in ("uz", "ru", "en")}

    if message.text not in driver_labels | passenger_labels:
        await message.answer(t(user_lang, "role.invalid"))
        return

    await message.answer(text=t(user_lang, "role.selected").format(role=message.text))

    if message.text in driver_labels:
        driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
        if driver:
            await state.clear()
            await message.answer(text=f"{t(user_lang, 'hello')}, {driver.firstname}👋", reply_markup=taxi_profile_keyboard(user_lang))
            await state.set_state(taxi_states.profile)
            return

        await message.answer(
            text=t(user_lang, "taxi.not_registered"),
            reply_markup=sign_up_keyboard(user_lang)
        )
        await state.set_state(taxi_states.firstname)
        return

    # Passenger
    await message.answer(t(user_lang, "passenger.hello"), reply_markup=passenger_keyboard(user_lang))
    await state.set_state(user_states.choose_option)


async def sign_up_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await message.answer(text=t(user_lang, "taxi.input.firstname"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.firstname)


async def get_firstname_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.update_data(firstname=message.text)
    await message.answer(t(user_lang, "taxi.input.lastname"))
    await state.set_state(taxi_states.lastname)


async def get_lastname_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.update_data(lastname=message.text)
    await message.answer(t(user_lang, "taxi.input.phone"), reply_markup=contact_keyboard(user_lang))
    await state.set_state(taxi_states.contact)

 
async def get_contact_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number
    else:
        phone = (message.text or "").strip()
    
    await state.update_data(phone_number=normalize_phone_number(phone) or phone)
    await message.answer(t(user_lang, "taxi.input.car_model"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.car_model)


async def get_car_model_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.update_data(car_model=message.text)
    await message.answer(t(user_lang, "taxi.input.car_number"))
    await state.set_state(taxi_states.car_number)


async def get_car_number_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.update_data(car_number=message.text)
    await message.answer(t(user_lang, "taxi.confirm"), reply_markup=taxi_confirm_keyboard(user_lang))
    await state.set_state(taxi_states.confirm)


async def confirm_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    data.pop('role', None)

    await crud_commands.add(model=models.Taxi, data=data)
    await message.answer(t(user_lang, "taxi.saved"), reply_markup=taxi_profile_keyboard(user_lang))
    await state.clear()
    await state.set_state(taxi_states.profile)


async def info_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    if not driver:
        await message.answer(t(user_lang, "taxi.not_registered"))
        return

    summary = (
        f"👤 <b>{t(user_lang, 'profile.info')}</b>\n"
        f"{t(user_lang, 'field.firstname')}: <b>{driver.firstname}</b>\n"
        f"{t(user_lang, 'field.lastname')}: <b>{driver.lastname}</b>\n"
        f"{t(user_lang, 'field.phone')}: <b>{driver.phone_number}</b>\n"
        f"{t(user_lang, 'field.car_model')}: <b>{driver.car_model}</b>\n"
        f"{t(user_lang, 'field.car_number')}: <b>{driver.car_number}</b>\n"
    )
    
    await message.answer(summary, parse_mode="HTML")


async def update_info_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await message.answer(t(user_lang, "profile.edit_menu"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)

async def back_to_edit_confirm(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    await message.answer(t(user_lang, "profile.edit_menu"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)

async def choose_edit_firstname(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})

    await message.answer(
        f"{t(user_lang, 'taxi.edit.firstname')}\n\n"
        f"<b>{t(user_lang, 'edit.current')}: {driver.firstname}</b>\n"
        f"{t(user_lang, 'edit.example')}: Ali",
        reply_markup=taxi_back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(taxi_states.edit_firstname)


async def choose_edit_lastname(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(
        f"{t(user_lang, 'taxi.edit.lastname')}\n\n"
        f"<b>{t(user_lang, 'edit.current')}: {driver.lastname}</b>\n"
        f"{t(user_lang, 'edit.example')}: Valiyev",
        reply_markup=taxi_back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(taxi_states.edit_lastname)


async def choose_edit_phone(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(
        f"{t(user_lang, 'taxi.edit.phone')}\n\n"
        f"<b>{t(user_lang, 'edit.current')}: {driver.phone_number}</b>\n"
        f"{t(user_lang, 'edit.example')}: +998901234567",
        reply_markup=taxi_back_and_phone_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(taxi_states.edit_phone)


async def choose_edit_car_model(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(
        f"{t(user_lang, 'taxi.edit.car_model')}\n\n"
        f"<b>{t(user_lang, 'edit.current')}: {driver.car_model}</b>\n"
        f"{t(user_lang, 'edit.example')}: Cobalt",
        reply_markup=taxi_back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(taxi_states.edit_car_model)


async def choose_edit_car_number(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(
        f"{t(user_lang, 'taxi.edit.car_number')}\n\n"
        f"<b>{t(user_lang, 'edit.current')}: {driver.car_number}</b>\n"
        f"{t(user_lang, 'edit.example')}: 01A123BC",
        reply_markup=taxi_back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(taxi_states.edit_car_number)


async def back_to_profile(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await message.answer(t(user_lang, "back.to_menu"), reply_markup=taxi_profile_keyboard(user_lang))
    await state.set_state(taxi_states.profile)


async def get_new_firstname_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'firstname': message.text})
    await message.answer(t(user_lang, "profile.updated"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)


async def get_new_lastname_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'lastname': message.text})
    await message.answer(t(user_lang, "profile.updated"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)


async def get_new_phone_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    phone = str(message.contact.phone_number) if message.contact and message.contact.phone_number else (message.text or "").strip()
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'phone_number': normalize_phone_number(phone) or phone})
    await message.answer(t(user_lang, "profile.updated"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)


async def get_new_car_model_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'car_model': message.text})
    await message.answer(t(user_lang, "profile.updated"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)


async def get_new_car_number_answer(message: Message, state: FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'car_number': message.text})
    await message.answer(t(user_lang, "profile.updated"), reply_markup=edit_profile_keyboard(user_lang))
    await state.set_state(taxi_states.edit_confirm)

async def complaints_start(message : Message, state : FSMContext):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    await state.clear()

    await message.answer(
        t(user_lang, "complaint.prompt"),
        reply_markup=taxi_back_keyboard(user_lang)
    )

    await state.set_state(taxi_states.complaint_text)

async def complaints_handler(message : Message, state : FSMContext, bot):
    user_lang = await UserService.get_user_language(str(message.from_user.id))
    
    ADMIN_CHAT_ID = -1003780044555

    user = message.from_user

    caption = (
        f"📩 Yangi shikoyat/taklif\n\n"
        f"👤 User: {user.full_name}\n"
        f"🆔 ID: {user.id}\n\n"
    )

    if message.text:
        text = caption + f"💬 Xabar:\n{message.text}"
        await bot.send_message(ADMIN_CHAT_ID, text)

    elif message.photo:
        photo = message.photo[-1].file_id
        text = caption + f"💬 Caption:\n{message.caption or 'Yo‘q'}"
        await bot.send_photo(ADMIN_CHAT_ID, photo, caption=text)

    elif message.video:
        video = message.video.file_id
        text = caption + f"💬 Caption:\n{message.caption or 'Yo‘q'}"
        await bot.send_video(ADMIN_CHAT_ID, video, caption=text)

    elif message.document:
        doc = message.document.file_id
        text = caption + f"💬 Caption:\n{message.caption or 'Yo‘q'}"
        await bot.send_document(ADMIN_CHAT_ID, doc, caption=text)

    await message.answer(t(user_lang, "complaint.accepted"), reply_markup=taxi_back_keyboard(user_lang))
    
