from aiogram.types import Message
from aiogram import Bot
from .keyboards import (
    show_role_buttons,
    sign_up,
    get_contact,
    confirm,
    taxi_profile,
    edit_profile
)

from aiogram.fsm.context import FSMContext
from .states import taxi_states
from user.keyboards import passenger_keyboard
from user.states import user_states
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from data import crud_commands, models


async def start_command_answer(message: Message, bot: Bot, state: FSMContext):
    await message.answer(text="Welcome to our bot, user!")
    await message.answer(
        text="Agar tilni o'zgartirmoqchi bo'lsangiz /language ni bosing.\n"
             "Aks holda davom eting (O'zbek tilida)."
    )
    await message.answer(text="Choose your role!", reply_markup=show_role_buttons)
    await state.clear()
    await state.set_state(taxi_states.choosing_role)


async def change_role_command_answer(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Choose your role!", reply_markup=show_role_buttons)
    await state.set_state(taxi_states.choosing_role)


async def to_choose_a_role_answer(message: Message, state: FSMContext):
    if message.text not in ["Passenger", "Driver"]:
        await message.answer("You need to choose your role matched on the keyboard!")
        return

    await message.answer(text=f"Your role is {message.text}!")

    if message.text == "Driver":
        driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
        if driver:
            await state.clear()
            await message.answer(text=f"Hello, {driver.firstname}👋", reply_markup=taxi_profile)
            return

        await message.answer(
            text="Driver, you're not registered yet!\nPlease sign up!",
            reply_markup=sign_up
        )
        await state.set_state(taxi_states.firstname)
        return

    # Passenger
    user_lang = "uz"
    await message.answer("choose.option", reply_markup=passenger_keyboard(user_lang))
    await state.set_state(user_states.choose_option)


async def sign_up_answer(message: Message, state: FSMContext):
    await message.answer(text="Please enter your firstname!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.firstname)


async def get_firstname_answer(message: Message, state: FSMContext):
    await state.update_data(firstname=message.text)
    await message.answer("Please enter your lastname!")
    await state.set_state(taxi_states.lastname)


async def get_lastname_answer(message: Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await message.answer("Please send your contact!", reply_markup=get_contact)
    await message.answer("Telefon raqamini ushbu formatlarda yuboring :\n       +998901234567 yoki 0901234567.")
    await state.set_state(taxi_states.contact)

 
async def get_contact_answer(message: Message, state: FSMContext):
    if message.contact and message.contact.phone_number:
        phone = str(message.contact.phone_number)
    else:
        phone = (message.text or "").strip()

    await state.update_data(phone_number=phone)
    await message.answer("Please enter your car model!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.car_model)


async def get_car_model_answer(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("Please enter your car number!")
    await message.answer("Mashina raqamini ushbu formatlarda kiriting :\n       41A111AA yoki 01A1234")
    await state.set_state(taxi_states.car_number)


async def get_car_number_answer(message: Message, state: FSMContext):
    await state.update_data(car_number=message.text)
    await message.answer("Please make sure your all information is right, and confirm!", reply_markup=confirm)
    await state.set_state(taxi_states.confirm)


async def confirm_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    data.pop('role', None)

    await crud_commands.add(model=models.Taxi, data=data)
    await message.answer("Your all information is saved ✅!", reply_markup=taxi_profile)
    await state.clear()


async def info_answer(message: Message, state: FSMContext):
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    if not driver:
        await message.answer("Siz ro'yxatdan o'tmagan ekansiz. Iltimos avval Sign up ni tanlang.")
        return

    summary = (
        f"👤 <b>Profil ma'lumotlari</b>\n"
        f"Ism: {driver.firstname}\n"
        f"Familiya: {driver.lastname}\n"
        f"Telefon: {driver.phone_number}\n"
        f"Mashina modeli: {driver.car_model}\n"
        f"Mashina raqami: {driver.car_number}\n"
    )
    summary += "\n\nO'zgartirish uchun quyidagi tugmalardan birini tanlang."
    await message.answer(summary, parse_mode="HTML")


async def update_info_answer(message: Message, state: FSMContext):
    await message.answer("You can change your information", reply_markup=edit_profile)
    await state.set_state(taxi_states.edit_confirm)


async def choose_edit_firstname(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Yangi ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_firstname)


async def choose_edit_lastname(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Yangi familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_lastname)


async def choose_edit_phone(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos telefon kontaktingizni yuboring yoki raqamingizni yozing:", reply_markup=get_contact)
    await state.set_state(taxi_states.edit_phone)


async def choose_edit_car_model(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Yangi mashina modelini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_car_model)


async def choose_edit_car_number(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Yangi mashina raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_car_number)


async def back_to_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyuga qaytildi.", reply_markup=taxi_profile)


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