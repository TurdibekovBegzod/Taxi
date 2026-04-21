# Here you need write your functions
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from .states import user_states
from taxi.states import taxi_states
from data.crud_commands import create_order
import os
from .keyboards import place_keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from user.keyboards import (
    language_keyboard,
    passenger_keyboard,
    confirm_keyboard,
    edit_keyboard,
    btn_back
)
from user.i18n import t
from user.keyboards import language_keyboard, passenger_keyboard,btn_phone_keyboard, confirm_keyboard, edit_keyboard, cancel_keyboard
from user.i18n import t

async def language_command(message: Message, state: FSMContext):
    user_lang = "uz"

    await message.answer(
        t(user_lang, "language.choose"),
        reply_markup=language_keyboard()
    )
    await state.set_state(taxi_states.choosing_role)

async def passenger_start(message: Message, state: FSMContext):
    await state.set_state(user_states.choose_option)

async def travel_start(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(user_states.user_firstname)

async def process_firstname(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    await state.update_data(user_firstname=message.text)
    await message.answer("Familiyangizni kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(user_states.user_lastname)


async def process_lastname(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    await state.update_data(user_lastname=message.text)
    await message.answer("Telefon raqamingizni  kiriting\nNamuna: 995673412  yoki +9981232321", reply_markup=btn_phone_keyboard)
    await state.set_state(user_states.user_phone)


async def process_phone(message: Message, state: FSMContext):
    await message.answer("Telefon raqamingiz qabul qilindi ✅", reply_markup=ReplyKeyboardRemove())

    if message.contact and message.contact.phone_number:
        phone = str(message.contact.phone_number)
    else:
        phone = (message.text or "").strip()

    await state.update_data(user_phone=phone)

    from .keyboards import place_keyboard
    await message.answer("Qayerdan ketasiz ?", reply_markup=place_keyboard("uz", type="from"))
    await state.set_state(user_states.user_place1)


async def process_location(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return

    if not message.location:
        await message.answer("📍 Iltimos lokatsiyani tugma orqali yuboring!")
        return
   

    data = await state.get_data()
    editing_field = data.get("editing_field")

    if editing_field == "user_location":

        await state.update_data(
            user_location=message.location
        )

        await state.update_data(editing_field=None)

        await show_order_summary(message, state)
        return

    await message.answer("Nechta odam ketadi? \nNamuna: 2", reply_markup=cancel_keyboard)
    await state.set_state(user_states.user_people)
    if await check_cancel(message, state):
        return
    await state.update_data(
        user_location=message.location
    )

async def show_order_summary(message: Message, state: FSMContext):
    
    data = await state.get_data()
    summary = (
        f"✅ Sizning so'rovingiz!\n\n"
        f"Ism: {data.get('user_firstname')}\n"
        f"Familiya: {data.get('user_lastname')}\n"
        f"Telefon: {data.get('user_phone')}\n"
        f"Qayerdan: {data.get('user_place1')}\n"
        f"Qayerga: {data.get('user_place2')}\n"
        f"Odamlar soni: {data.get('user_people')}\n\n"
    )

    await message.answer(summary, reply_markup=confirm_keyboard("uz"))
    await state.set_state(user_states.confirm_order)

async def process_people(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    people_count = message.text.strip()
    
    if not people_count.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting!\nMasalan: 5")
        return 

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
        f"Odamlar soni: {data.get('user_people', '')}"
    )

    SUPERADMIN = int(os.getenv("SUPERADMIN"))
    await bot.send_message(SUPERADMIN, summary)
    new_order = await create_order(message=summary, user_id = int(message.from_user.id))
    await send_order_to_channel(bot, state, order_id=new_order.uid, user_id = message.from_user.id)

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

async def show_edit_menu(message: Message, state: FSMContext):
    await message.answer(
        "Qaysi ma'lumotni o‘zgartirmoqchisiz?",
        reply_markup=edit_keyboard("uz")
    )
    await state.set_state(user_states.edit_field)

async def choose_edit_field(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    if message.text == "⬅️ Orqaga":
        await show_order_summary(message, state)
        return
    if message.text == "Ism":
        await edit_firstname_start(message, state)
    elif message.text == "Familiya":
        await edit_lastname_start(message, state)
    elif message.text == "Telefon":
        await edit_phone_start(message, state)
    elif message.text == "Qayerdan":
        await edit_place1_start(message, state)
    elif message.text == "Qayerga":
        await edit_place2_start(message, state)
    elif message.text == "Lokatsiya":
        await edit_location_start(message, state)
    elif message.text == "Odamlar soni":
        await edit_people_start(message, state)
    else:
        await message.answer("Iltimos, tugmalardan birini tanlang.")

async def edit_firstname_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_name = data.get('user_firstname', '')    
    back_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )
    
    await message.answer(
        f"✏️ Yangi ismingizni kiriting:\n\n📌 Hozirgi ismingiz: {current_name}",
        reply_markup=back_keyboard
    )
    await state.set_state(user_states.editing_firstname)

async def edit_firstname_save(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await show_edit_menu(message, state)
        return
    new_name = message.text.strip()
    if not new_name:
        await message.answer("❌ Ism kiritilmadi. Qaytadan kiriting:")
        return
    
    await state.update_data(user_firstname=new_name)
    await show_order_summary(message, state)

async def edit_lastname_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_lastname = data.get('user_lastname', '')
    
    back_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )
    
    await message.answer(
        f"✏️ Yangi familiyangizni kiriting:\n\n📌 Hozirgi familiyangiz: {current_lastname}",
        reply_markup=back_keyboard
    )
    await state.set_state(user_states.editing_lastname)

async def edit_lastname_save(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await show_edit_menu(message, state)
        return
    
    new_lastname = message.text.strip()
    if not new_lastname:
        await message.answer("❌ Familiya kiritilmadi. Qaytadan kiriting:")
        return
    
    await state.update_data(user_lastname=new_lastname)
    await show_order_summary(message, state)


async def edit_phone_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_phone = data.get('user_phone', '')
    
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqam yuborish", request_contact=True)],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"✏️ Yangi telefon raqamingizni kiriting:\n\n📌 Hozirgi raqam: {current_phone}",
        reply_markup=phone_keyboard
    )
    await state.set_state(user_states.editing_phone)

async def edit_phone_save(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await show_edit_menu(message, state)
        return
    
    if message.contact and message.contact.phone_number:
        new_phone = str(message.contact.phone_number)
    else:
        new_phone = message.text.strip()
    
    if not new_phone:
        await message.answer("❌ Telefon raqam kiritilmadi. Qaytadan kiriting:")
        return
    
    await state.update_data(user_phone=new_phone)
    await show_order_summary(message, state)

async def edit_place1_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_place = data.get('user_place1', '')
    
    await message.answer(
        f"✏️ Jo'nash viloyatini tanlang:\n\n📌 Hozirgi: {current_place}",
        reply_markup=place_keyboard("uz", "from")
    )

async def edit_place1_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data.startswith("place1_"):
        place = data.split("_", 1)[1]
        await state.update_data(user_place1=place)
        await show_order_summary(callback.message, state)
        await callback.answer()
        await callback.message.delete()


async def edit_place2_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_place = data.get('user_place2', '')
    
    await message.answer(
        f"✏️ Borish viloyatini tanlang:\n\n📌 Hozirgi: {current_place}",
        reply_markup=place_keyboard("uz", "to")
    )

async def edit_place2_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data.startswith("place2_"):
        place = data.split("_", 1)[1]
        await state.update_data(user_place2=place)
        await show_edit_menu(callback.message, state)
        await callback.answer()
        await callback.message.delete()

async def edit_location_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_location = data.get('user_location')    
    location_text = "❌ Lokatsiya yo'q"
    if current_location:
        location_text = f"📍 Lokatsiya bor"
    
    location_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"✏️ Yangi lokatsiyangizni yuboring:\n\n📌 Hozirgi: {location_text}",
        reply_markup=location_keyboard
    )
    await state.set_state(user_states.editing_location)

async def edit_location_save(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await show_edit_menu(message, state)
        return
    
    if not message.location:
        await message.answer("📍 Iltimos, lokatsiyani tugma orqali yuboring!")
        return
    
    await state.update_data(user_location=message.location)
    await show_order_summary(message, state)


async def edit_people_start(message: Message, state: FSMContext):
    data = await state.get_data()
    current_people = data.get('user_people', '')
    
    back_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )
    
    await message.answer(
        f"✏️ Yangi odamlar sonini kiriting:\n\n📌 Hozirgi son: {current_people}\n📝 Namuna: 2, 3, 4",
        reply_markup=back_keyboard
    )
    await state.set_state(user_states.editing_people)

async def edit_people_save(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await show_edit_menu(message, state)
        return
    
    people_count = message.text.strip()
    
    if not people_count.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting!\nMasalan: 5")
        return
    
    await state.update_data(user_people=int(people_count))
    await show_order_summary(message, state)



CHANNEL_ID = "@taxi_test_uz"
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from user.keyboards import receive

async def send_order_to_channel(bot: Bot, state: FSMContext, order_id, user_id):
    data = await state.get_data()
    
    location = data.get("user_location")
    
    map_link = ""
    if location:
        map_link = f"https://maps.google.com/?q={location.latitude},{location.longitude}"

    text = f"""
            🚕 YANGI BUYURTMA #{order_id}

            👤 Ism: {data.get('user_firstname')}
            👤 Familiya: {data.get('user_lastname')}
            📞 Telefon: cho{data.get('user_phone')}

            📍 Qayerdan: {data.get('user_place1')}
            📍 Qayerga: {data.get('user_place2')}

            👥 Odamlar: {data.get('user_people')}
            📍 Lokatsiya:
            {map_link}
            """

    msg = await bot.send_message(
        CHANNEL_ID,
        text,
        reply_markup=receive(order_id, user_id)  
    )

    if location:
        loc_msg = await bot.send_location(
            CHANNEL_ID,
            latitude=location.latitude,
            longitude=location.longitude
        )
        from data.crud_commands import update
        from data.models import Order
        await update(Order, {"uid": order_id}, {
            "message": text,
            "lat": location.latitude if location else None,
            "lon": location.longitude if location else None,
            "location_message_id": loc_msg.message_id if location else None
        })


    await state.update_data(order_id=order_id)
    return order_id
       
async def channel_handler(message):
    link = "https://t.me/taxi_test_uz"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanal", url=link)]
        ]
    )

    await message.answer(
        f"📢 Shu link orqali kanalga o'tishingiz mumkin:\n{link}",
        reply_markup=keyboard
    )

async def complaints_start(message, state):
    await state.clear()

    await message.answer(
        "✍️ Shikoyat va takliflaringizni yuborishingiz mumkin.",
        reply_markup=btn_back
    )

    await state.set_state(user_states.complaint_text)

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
    

async def back_to_choose_option(message : Message, state : FSMContext):
    await state.clear()

    user_lang = "uz"
    await message.answer("Asosiy menyuga qaytildi.", reply_markup=passenger_keyboard(user_lang))

    await state.set_state(user_states.choose_option)

async def check_cancel(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi",
            reply_markup=passenger_keyboard("uz")
        )
        await state.set_state(user_states.choose_option)
        return True
    return False
