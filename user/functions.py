# Here you need write your functions
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from .states import user_states
from taxi.states import taxi_states
import os


from user.keyboards import language_keyboard, passenger_keyboard
from user.i18n import t

# ======================
# /language komandasi
async def language_command(message: Message, state: FSMContext):
    # hozircha default til
    user_lang = "uz"

    await message.answer(
        t(user_lang, "language.choose"),
        reply_markup=language_keyboard()
    )
    await state.set_state(taxi_states.choosing_role)

async def passenger_start(message: Message, state: FSMContext):
    user_lang = "uz"  # Bu yerda foydalanuvchining tanlagan tilini olishingiz mumkin
    await message.answer(
        t(user_lang, "choose.option"),  # Masalan, "Quyidagi bo‘limlardan birini tanlang:"
        reply_markup=passenger_keyboard(user_lang)
    )
    await state.set_state(user_states.choose_option)



# ======================
# Sayohat tugmasi bosilganda FSM boshlash
async def travel_start(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(user_states.user_firstname)

# ======================
# 1. Ism qabul qilish
async def process_firstname(message: Message, state: FSMContext):
    await state.update_data(user_firstname=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(user_states.user_lastname)

# ======================
# 2. Familiya qabul qilish
async def process_lastname(message: Message, state: FSMContext):
    await state.update_data(user_lastname=message.text)
    await message.answer("Raqamingizni kiriting:")
    await state.set_state(user_states.user_phone)

# ======================
# 3. Telefon raqamini qabul qilish
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(user_phone=message.text)
    # Inline keyboard callback Qayerdan uchun
    from .keyboards import place_keyboard
    await message.answer("Qayerdan?", reply_markup=place_keyboard("uz", type="from"))
    await state.set_state(user_states.user_place1)

# ======================
# 6. Lokatsiya qabul qilish
async def process_location(message: Message, state: FSMContext):
    if not message.location:
        await message.answer("📍 Iltimos lokatsiyangizni yuboring!")
        return
    await state.update_data(user_location=message.location)
    await message.answer("Qachon ketmoqchisiz? Sana va vaqtni kiriting (YYYY-MM-DD HH:MM):")
    await state.set_state(user_states.user_time)

# ======================
# 7. Sana va vaqt qabul qilish
async def process_time(message: Message, state: FSMContext):
    await state.update_data(user_time=message.text)
    await message.answer("Nechta odam ketadi?")
    await state.set_state(user_states.user_people)

# ======================
# 8. Odamlar soni qabul qilish va yakunlash
async def process_people(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(user_people=message.text)

    data = await state.get_data()
    summary = (
        f"✅ So'rovingiz qabul qilindi!\n\n"
        f"Ism: {data.get('user_firstname')}\n"
        f"Familiya: {data.get('user_lastname')}\n"
        f"Telefon: {data.get('user_phone')}\n"
        f"Qayerdan: {data.get('user_place1')}\n"
        f"Qayerga: {data.get('user_place2')}\n"
        f"Sana va vaqt: {data.get('user_time')}\n"
        f"Odamlar soni: {data.get('user_people')}\n\n"
        f"Haydovchilarimiz siz bilan bog'lanadi 🚖"
    )

    await message.answer(summary, reply_markup=passenger_keyboard("uz"))

    # Adminga jo'natish
    SUPERADMIN = int(os.getenv("SUPERADMIN"))
    await bot.send_message(SUPERADMIN, f"Yangi so'rov:\n{summary}")

    await state.clear()




# ==============================================
# Endi Mening so'rovlarim qismini yozamiz

