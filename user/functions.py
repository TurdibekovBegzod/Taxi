# Here you need write your functions
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from .states import user_states
from taxi.states import taxi_states
from data.crud_commands import create_order
import os


from user.keyboards import (
    language_keyboard,
    passenger_keyboard,
    confirm_keyboard,
    edit_keyboard
)
from user.i18n import t

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
    await message.answer("Telefon raqamingizni  kiriting\nNamuna: 995673412  yoki +9981232321")
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

    # agar lokatsiya yuborilmasa
    if not message.location:
        await message.answer("📍 Iltimos lokatsiyani tugma orqali yuboring!")
        return

    data = await state.get_data()
    editing_field = data.get("editing_field")

    # =====================
    # locatsiya tahrirlansa
    if editing_field == "user_location":

        await state.update_data(
            user_location=message.location
        )

        # editing flagni tozalash
        await state.update_data(editing_field=None)

        # qayta summary ko'rsatish
        await show_order_summary(message, state)

        return

    # =====================
    # ODDIY BUYURTMA JARAYONI
    await state.update_data(
        user_location=message.location
    )

    await message.answer(
        "🕒 Qachon ketmoqchisiz?\n📅 Namuna: 25.03.2026 14:30 "
    )

    await state.set_state(user_states.user_time)# ======================
# 7. Sana va vaqt qabul qilish
async def process_time(message: Message, state: FSMContext):
    await state.update_data(user_time=message.text)
    await message.answer("Nechta odam ketadi? \n Namuna: 2")
    await state.set_state(user_states.user_people)

# ======================
# 8. Odamlar soni qabul qilish va yakunlash
async def show_order_summary(message: Message, state: FSMContext):
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
    )

    await message.answer(summary, reply_markup=confirm_keyboard("uz"))
    await state.set_state(user_states.confirm_order)


async def process_people(message: Message, state: FSMContext):
    people_count = message.text.strip()
    
    # Faqat raqam ekanligini tekshirish
    if not people_count.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting!\nMasalan: 5")
        return  # Qayta kiritish uchun to'xtatish
    
    # Ma'lumotni saqlash
    await state.update_data(user_people=int(people_count))
    await show_order_summary(message, state)


async def confirm_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    summary = (
        f"🚖 Yangi so'rov:\n\n"
        f"Ism: {data.get('user_firstname', '')}\n"
        f"Familiya: {data.get('user_lastname', '')}\n"
        f"Telefon: {data.get('user_phone', '')}\n"
        f"Qayerdan: {data.get('user_place1', '')}\n"
        f"Qayerga: {data.get('user_place2', '')}\n"
        f"Sana va vaqt: {data.get('user_time', '')}\n"
        f"Odamlar soni: {data.get('user_people', '')}"
    )

    SUPERADMIN = int(os.getenv("SUPERADMIN"))
    await bot.send_message(SUPERADMIN, summary)
    new_order = await create_order(message=summary, user_id = message.from_user.id)
    # user_id = message.from_user.id

    # await send_order_to_group(bot, state)
    from .functions import send_order_to_channel

    await send_order_to_channel(bot, state, order_id=new_order.uid)

    await message.answer(
        "✅ So‘rovingiz yuborildi.\n\nHaydovchilarimiz siz bilan bog'lanadi 🚖",
        reply_markup=passenger_keyboard("uz")
    )

    await state.set_state(user_states.choose_option)


async def cancel_order(message: Message, state: FSMContext):
    
    await message.answer(
        "❌ Buyurtma bekor qilindi.",
        reply_markup=passenger_keyboard("uz")
    )

    await state.set_state(user_states.choose_option)

async def edit_order(message: Message, state: FSMContext):
    await message.answer(
        "Qaysi ma'lumotni o‘zgartirmoqchisiz?",
        reply_markup=edit_keyboard("uz")
    )
    await state.set_state(user_states.edit_field)


async def choose_edit_field(message: Message, state: FSMContext):
    from .keyboards import place_keyboard
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

    if message.text == "⬅️ Orqaga":
        await show_order_summary(message, state)
        return

    # QAYERDAN
    if message.text == "Qayerdan":
        await state.update_data(editing_field="user_from")

        await message.answer(
            "Jo'nash viloyatini tanlang:",
            reply_markup=place_keyboard("uz", "from")
        )

        await state.set_state(user_states.user_place1)
        return

    # QAYERGA
    if message.text == "Qayerga":
        await state.update_data(editing_field="user_to")

        await message.answer(
            "Borish viloyatini tanlang:",
            reply_markup=place_keyboard("uz", "to")
        )

        await state.set_state(user_states.user_place2)
        return

    # LOKATSIYA
    if message.text == "Lokatsiya":
        location_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]
            ],
            resize_keyboard=True
        )

        await state.update_data(editing_field="user_location")

        await message.answer(
            "📍 Lokatsiyangizni yuboring:",
            reply_markup=location_keyboard
        )

        await state.set_state(user_states.user_location)
        return
    
    field_map = {
        "Ism": ("user_firstname", "Yangi ismingizni kiriting:"),
        "Familiya": ("user_lastname", "Yangi familiyangizni kiriting:"),
        "Telefon": ("user_phone", "Yangi telefon raqamingizni kiriting:"),
        "Sana va vaqt": ("user_time", "Yangi sana va vaqtni kiriting (YYYY-MM-DD HH:MM):"),
        "Odamlar soni": ("user_people", "Yangi odamlar sonini kiriting:")
    }

    if message.text not in field_map:
        await message.answer("Iltimos, tugmalardan birini tanlang.")
        return

    field_name, ask_text = field_map[message.text]

    await state.update_data(editing_field=field_name)
    await message.answer(
        ask_text,
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(user_states.edit_value)
async def save_edited_value(message: Message, state: FSMContext,bot:Bot):
    data = await state.get_data()
    editing_field = data.get("editing_field")

    if not editing_field:
        await message.answer("Xatolik yuz berdi. Qaytadan urinib ko‘ring.")
        await state.clear()
        return

    if editing_field == "user_location":
        if not message.location:
            await message.answer("📍 Iltimos, lokatsiyani tugma orqali yuboring.")
            return

        await state.update_data(user_location=message.location)
        await show_order_summary(message, state)
        return

    await state.update_data(**{editing_field: message.text})
    await show_order_summary(message, state)

CHANNEL_ID = "@taxi_test_uz"
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from user.keyboards import receive
from user.callback import location_messages, order_texts, order_locations, location_messages

CHANNEL_ID = "@taxi_test_uz"

async def send_order_to_channel(bot: Bot, state: FSMContext, order_id):
    data = await state.get_data()
    
    location = data.get("user_location")

    
    map_link = ""
    if location:
        map_link = f"https://maps.google.com/?q={location.latitude},{location.longitude}"

    # Yo'lovchi ma'lumotlarini saqlash (order_id bo'yicha)
    # Bu yerda xohlasangiz dictionary ga saqlashingiz mumkin
    # Masalan: orders[order_id] = {"phone": data.get('user_phone'), "telegram_id": data.get('user_telegram_id')}

    text = f"""
🚕 YANGI BUYURTMA #{order_id}

👤 Ism: {data.get('user_firstname')}
📞 Telefon: {data.get('user_phone')}

📍 Qayerdan: {data.get('user_place1')}
📍 Qayerga: {data.get('user_place2')}

👥 Odamlar: {data.get('user_people')}
🕒 Vaqt: {data.get('user_time')}

📍 Lokatsiya:
{map_link}
"""


    # Asosiy xabar
    msg = await bot.send_message(
        CHANNEL_ID,
        text,
        reply_markup=receive(order_id)  
    )

    # Lokatsiya xabari
    if location:
        loc_msg = await bot.send_location(
            CHANNEL_ID,
            latitude=location.latitude,
            longitude=location.longitude
        )
        location_messages[str(order_id)] = loc_msg.message_id

        order_locations[str(order_id)] = (location.latitude, location.longitude)

    order_texts[str(order_id)] = text

    await state.update_data(order_id=order_id)
    return order_id

        
async def channel_handler(message):
    link = "https://t.me/taxi_test_uz"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Guruhga o'tish", url=link)]
        ]
    )

    await message.answer(
        f"📢 Shu link orqali guruhga o'tishingiz mumkin:\n{link}",
        reply_markup=keyboard
    )


async def complaints_start(message, state):
    await state.set_state(user_states.complaint_text)

    await message.answer(
        "✍️ Shikoyat va takliflaringizni yuborishingiz mumkin.\n\n"
        " Faqat hammasini bitta yozishda Yozib yuboring 👇"
    )

async def complaints_handler(message, state, bot):
    ADMIN_CHAT_ID = -1003780044555 

    user = message.from_user

    text = (
        f"📩 Yangi shikoyat/taklif\n\n"
        f"👤 User: {user.full_name}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Xabar:\n{message.text}"
    )

    await bot.send_message(ADMIN_CHAT_ID, text)

    await message.answer("✅ Xabaringiz qabul qilindi. Rahmat!")

    await state.clear()  # holatni tozalash



