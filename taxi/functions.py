from aiogram.types import Message
from aiogram import Bot
from .keyboards import (
    show_role_buttons,
    sign_up,
    get_contact,
    confirm,
    taxi_profile,
    edit_profile,
    btn_back,
    btn_back_and_phone
)

from aiogram.fsm.context import FSMContext
from .states import taxi_states
from user.keyboards import passenger_keyboard
from user.states import user_states
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from data import crud_commands, models


async def start_command_answer(message: Message, bot: Bot, state: FSMContext):
    await message.answer(text="Botimizga xush kelibsiz\n\nRolingizni tanlang!", reply_markup=show_role_buttons)
    await state.clear()
    await state.set_state(taxi_states.choosing_role)


async def change_role_command_answer(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Rolingizni tanlang!", reply_markup=show_role_buttons)
    await state.set_state(taxi_states.choosing_role)


async def to_choose_a_role_answer(message: Message, state: FSMContext):
    if message.text not in ["👤 Yo'lovchi", "🚖 Haydovchi"]:
        await message.answer("Klaviaturadagi harflarga mos ravishda rolingizni tanlang")
        return

    await message.answer(text=f"Sizning rolingiz  {message.text}!")

    if message.text == "🚖 Haydovchi":
        driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
        if driver:
            await state.clear()
            await message.answer(text=f"Salom, {driver.firstname}👋", reply_markup=taxi_profile)
            await state.set_state(taxi_states.profile)
            return

        await message.answer(
            text="Haydovchi, siz hali ro‘yxatdan o‘tmagansiz!\nIltimos, ro‘yxatdan o‘ting!",
            reply_markup=sign_up
        )
        await state.set_state(taxi_states.firstname)
        return

    # Passenger
    user_lang = "uz"
    await message.answer("Salom yo'lovchi 👋", reply_markup=passenger_keyboard(user_lang))
    await state.set_state(user_states.choose_option)


async def sign_up_answer(message: Message, state: FSMContext):
    await message.answer(text="Iltimos ismingizni kiriting!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.firstname)


async def get_firstname_answer(message: Message, state: FSMContext):
    await state.update_data(firstname=message.text)
    await message.answer("Iltimos familiyangizni kiriting!")
    await state.set_state(taxi_states.lastname)


async def get_lastname_answer(message: Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await message.answer("Iltimos, kontaktni yuboring!", reply_markup=get_contact)
    await message.answer("Telefon raqamini ushbu formatlarda yuboring :\n+998901234567 yoki 901234567 bu ko'rinishda.")
    await state.set_state(taxi_states.contact)

 
async def get_contact_answer(message: Message, state: FSMContext):
    if message.contact and message.contact.phone_number:
        phone = str(message.contact.phone_number)
    else:
        phone = (message.text or "").strip()

    await state.update_data(phone_number=phone)
    await message.answer("Iltimos, mashinangiz modelini kiriting!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.car_model)


async def get_car_model_answer(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("Iltimos, mashinangiz raqamini kiriting!")
    await state.set_state(taxi_states.car_number)


async def get_car_number_answer(message: Message, state: FSMContext):
    await state.update_data(car_number=message.text)
    await message.answer("Iltimos, barcha ma’lumotlaringiz to‘g‘ri ekanligini tekshiring va tasdiqlang!", reply_markup=confirm)
    await state.set_state(taxi_states.confirm)


async def confirm_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    data.pop('role', None)

    await crud_commands.add(model=models.Taxi, data=data)
    await message.answer("Barcha ma’lumotlaringiz saqlandi ✅!", reply_markup=taxi_profile)
    await state.clear()


async def info_answer(message: Message, state: FSMContext):
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    if not driver:
        await message.answer("Siz ro'yxatdan o'tmagan ekansiz. Iltimos avval 'Ro‘yxatdan o‘tish' ni tanlang.")
        return

    summary = (
        f"👤 <b>Profil ma'lumotlari</b>\n"
        f"Ism: <b>{driver.firstname}</b>\n"
        f"Familiya: <b>{driver.lastname}</b>\n"
        f"Telefon: <b>{driver.phone_number}</b>\n"
        f"Mashina modeli: <b>{driver.car_model}</b>\n"
        f"Mashina raqami: <b>{driver.car_number}</b>\n"
    )
    
    await message.answer(summary, parse_mode="HTML")


async def update_info_answer(message: Message, state: FSMContext):
    await message.answer("Ma’lumotlaringizni o‘zgartirishingiz mumkin", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)

async def back_to_edit_confirm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ma’lumotlaringizni o‘zgartirishingiz mumkin", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)

async def choose_edit_firstname(message: Message, state: FSMContext):
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})

    await message.answer(f"Sizning ismingiz <b>{driver.firstname}</b>\n"
                         f"Yangi ismingizni kiriting:", reply_markup=btn_back, parse_mode="HTML")
    await state.set_state(taxi_states.edit_firstname)


async def choose_edit_lastname(message: Message, state: FSMContext):
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(f"Sizning familiyangiz <b>{driver.lastname}</b>\n"
                         f"Yangi familiyangizni kiriting:", reply_markup=btn_back, parse_mode="HTML")
    await state.set_state(taxi_states.edit_lastname)


async def choose_edit_phone(message: Message, state: FSMContext):
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(f"Sizning telefon raqamingiz <b>{driver.phone_number}</b>\n"
                         f"Yangi telefon raqamingizni kiriting:", reply_markup=btn_back_and_phone, parse_mode="HTML")
    await state.set_state(taxi_states.edit_phone)


async def choose_edit_car_model(message: Message, state: FSMContext):
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(f"Sizning mashina modelingiz <b>{driver.car_model}</b>\n"
                         f"Yangi mashina modelini kiriting:", reply_markup=btn_back, parse_mode="HTML")
    await state.set_state(taxi_states.edit_car_model)


async def choose_edit_car_number(message: Message, state: FSMContext):
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    await message.answer(f"Sizning mashina raqamingiz <b>{driver.car_number}</b>\n"
                         f"Yangi mashina raqamini kiriting:", reply_markup=btn_back, parse_mode="HTML")
    await state.set_state(taxi_states.edit_car_number)


async def back_to_profile(message: Message, state: FSMContext):
    await message.answer("Asosiy menyuga qaytildi.", reply_markup=taxi_profile)
    await state.set_state(taxi_states.profile)


async def get_new_firstname_answer(message: Message, state: FSMContext):
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'firstname': message.text})
    await message.answer("Ismingiz yangilandi ✅", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)


async def get_new_lastname_answer(message: Message, state: FSMContext):
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'lastname': message.text})
    await message.answer("Familiyangiz yangilandi ✅", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)


async def get_new_phone_answer(message: Message, state: FSMContext):
    phone = str(message.contact.phone_number) if message.contact and message.contact.phone_number else (message.text or "").strip()
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'phone_number': phone})
    await message.answer("Telefon raqamingiz yangilandi ✅", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)


async def get_new_car_model_answer(message: Message, state: FSMContext):
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'car_model': message.text})
    await message.answer("Mashina modelingiz yangilandi ✅", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)


async def get_new_car_number_answer(message: Message, state: FSMContext):
    await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, {'car_number': message.text})
    await message.answer("Mashina raqamingiz yangilandi ✅", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)

async def complaints_start(message : Message, state : FSMContext):
    await state.clear()

    await message.answer(
        "✍️ Shikoyat va takliflaringizni yuborishingiz mumkin.",
        reply_markup=btn_back
    )

    await state.set_state(taxi_states.complaint_text)

async def complaints_handler(message : Message, state : FSMContext, bot):
    
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

    await message.answer("✅ Xabaringiz qabul qilindi. Rahmat!", reply_markup=btn_back)
    