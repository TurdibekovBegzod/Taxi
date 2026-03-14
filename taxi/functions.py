# Here you need write your functions
from aiogram.types import Message
from aiogram import Bot
from .keyboards import (
                        show_role_buttons, 
                        sign_up,
                        get_contact,
                        confirm,
                        taxi_profile)

from aiogram.fsm.context import FSMContext
from .states import taxi_states
from user.keyboards import passenger_keyboard
from user.states import user_states
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from data import crud_commands, models


async def start_command_answer(message : Message, bot : Bot, state : FSMContext):
    await message.answer(text = "Welcome to our bot, user!")
    # 2. Til haqidagi eslatma 
    await message.answer(
        text="Agar tilni o'zgartirmoqchi bo'lsangiz /language ni bosing.\n"
             "Aks holda davom eting (O'zbek tilida)."
    )
    await message.answer(text = "Choose your role!", reply_markup=show_role_buttons)
    await state.clear() # clear the state
    await state.set_state(taxi_states.choosing_role) # turn on the <choosing_role> state in taxi_states

async def change_role_command_answer(message : Message, state : FSMContext):
    await state.clear()
    await message.answer(text = "Choose your role!", reply_markup=show_role_buttons)
    await state.set_state(taxi_states.choosing_role) # turn on the <choosing_role> state in taxi_states


async def to_choose_a_role_answer(message : Message, state : FSMContext):
    if not(message.text == "Passenger" or message.text == "Driver"):
        await message.answer("You need to choose your role matched on the keyboard!")
        return
    
    if not taxi_states.choosing_role:
        return
    
    await message.answer(text = f"Your role is {message.text}!")

    if message.text == "Driver":
        driver = await crud_commands.get(models.Taxi, {"telegram_id" : message.from_user.id})
        
        if driver:
            # already registered; clear state so subsequent commands like Info/Update work
            await state.clear()
            await message.answer(text = f"Hello, {driver.firstname}👋", reply_markup=taxi_profile)
            return # Agar taxi ro'yxatdan o'tgan bo'lsa, keyingi kodlar ishlamasligi uchun return qilamiz
        
        await message.answer(text = """Driver, you're not registered yet!
                             \nPlease sign up!""",
                             reply_markup=sign_up)
        await state.set_state(taxi_states.firstname)
    else:
        user_lang = "uz"  # Bu yerda foydalanuvchining tanlagan tilini olishingiz mumkin
        await message.answer(
            "choose.option",  # Masalan, "Quyidagi bo‘limlardan birini tanlang:"
            reply_markup=passenger_keyboard(user_lang)
        )
        await state.set_state(user_states.choose_option)

    await state.update_data(role = message.text)
    # await state.set_state(None) # turn off the state
    # await state.set_state(user_states.choose_option)

async def sign_up_answer(message : Message, state : FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer(text = "Your're not right place !")
        return
    await message.answer(text = "Please enter your firstname!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.firstname)

async def get_firstname_answer(message : Message, state : FSMContext):
    await message.answer(f"Your name is {message.text}")
    await message.answer("Please enter your lastname!")
    await state.update_data(firstname = message.text)
    await state.set_state(taxi_states.lastname)

async def get_lastname_answer(message : Message, state : FSMContext):
    await message.answer(f"Your lastname is {message.text}")
    await state.update_data(lastname = message.text)
    await message.answer("Please send your contact!", reply_markup=get_contact)
    await state.set_state(taxi_states.contact)

async def get_contact_answer(message : Message, state : FSMContext):
    await message.answer("Your contact is taked!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Please enter your car model!")
    await state.update_data(phone_number = str(message.contact.phone_number))
    await state.set_state(taxi_states.car_model)

async def get_car_model_answer(message : Message, state : FSMContext):
    await message.answer(f"Your car model is {message.text}")
    await message.answer("Please enter you car number!")
    await state.update_data(car_model = message.text)
    await state.set_state(taxi_states.car_number)

async def get_car_number_answer(message : Message, state : FSMContext):
    data = await state.get_data()

    
    await message.answer(f"Your car number is {message.text}!")
    await state.update_data(car_number = message.text)
    await message.answer("""Please make sure your all information is right, and confirm!""", reply_markup=confirm)
    
    await state.set_state(taxi_states.confirm)

async def confirm_answer(message : Message, state : FSMContext):
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    data.pop('role', None)
    await crud_commands.add(
        model=models.Taxi, 
        data=data
    )

    await message.answer("Your all information is saved ✅!", reply_markup=taxi_profile)
    await state.clear()


# ------- new handlers for info and updates ---------

async def info_answer(message: Message, state: FSMContext):
    """Show current driver information. """
    await state.clear()
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
    # inform about update option
    summary += "\nAgar ma'lumotni yangilamoqchi bo'lsangiz 'Update info' tugmasini bosing."
    await message.answer(summary, parse_mode="HTML", reply_markup=taxi_profile)


async def update_info_answer(message: Message, state: FSMContext):
    """Start full-profile edit sequence."""
    await state.clear()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    if not driver:
        await message.answer("Siz ro'yxatdan o'tmagan ekansiz. Iltimos avval Sign up ni tanlang.")
        return

    # begin by asking for firstname
    await message.answer("Yangi ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_firstname)


async def get_new_firstname_answer(message: Message, state: FSMContext):
    await state.update_data(firstname=message.text)
    await message.answer("Yangi familiyangizni kiriting:")
    await state.set_state(taxi_states.edit_lastname)


async def get_new_lastname_answer(message: Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await message.answer("Iltimos kontaktni yuboring:", reply_markup=get_contact)
    await state.set_state(taxi_states.edit_phone)


async def get_new_phone_answer(message: Message, state: FSMContext):
    # expecting a contact object
    if not message.contact or not message.contact.phone_number:
        await message.answer("Iltimos pastdagi tugma orqali telefon raqamingizni yuboring:", reply_markup=get_contact)
        return
    await state.update_data(phone_number=str(message.contact.phone_number))
    await message.answer("Yangi mashina modelini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.edit_car_model)


async def get_new_car_model_answer(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("Yangi mashina raqamini kiriting:")
    await state.set_state(taxi_states.edit_car_number)


async def get_new_car_number_answer(message: Message, state: FSMContext):
    await state.update_data(car_number=message.text)
    await message.answer("Ma'lumotlaringiz yangilanadi. Tasdiqlaysizmi?", reply_markup=confirm)
    await state.set_state(taxi_states.edit_confirm)


async def confirm_edit_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    driver = await crud_commands.get(models.Taxi, {"telegram_id": message.from_user.id})
    if not driver:
        await message.answer("Tizimda xatolik yuz berdi, qayta urinib ko'ring.")
        await state.clear()
        return

    # collect all possible updates
    update_data = {}
    for field in ('firstname', 'lastname', 'phone_number', 'car_model', 'car_number'):
        if data.get(field):
            update_data[field] = data[field]

    if update_data:
        await crud_commands.update(models.Taxi, {'telegram_id': message.from_user.id}, update_data)

    await message.answer("Sizning ma'lumotlaringiz muvaffaqiyatli yangilandi ✅", reply_markup=taxi_profile)
    await state.clear()






        
