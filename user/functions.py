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
from user.keyboards import (
    language_keyboard,
    passenger_keyboard,
    phone_keyboard,
    location_keyboard,
    back_keyboard,
    confirm_keyboard,
    edit_keyboard,
    cancel_keyboard,
    cancel_keyboard_for,
)
from user.i18n import t
from services.phone import normalize_phone_number
from services.users import UserService

REQUIRED_ORDER_FIELDS = {
    "user_firstname": "Ism",
    "user_lastname": "Familiya",
    "user_phone": "Telefon",
    "user_place1": "Qayerdan",
    "user_place2": "Qayerga",
    "user_location": "Lokatsiya",
    "user_people": "Odamlar soni",
}
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from user.keyboards import receive

load_dotenv()


CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))


def get_missing_order_fields(data: dict) -> list[str]:
    missing = []

    for key, label in REQUIRED_ORDER_FIELDS.items():
        value = data.get(key)
        if value is None or value == "":
            missing.append(label)

    return missing


async def get_user_lang(message: Message) -> str:
    return await UserService.get_user_language(str(message.from_user.id))


async def language_command(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    current_state = await state.get_state()
    if current_state != user_states.choosing_language.state:
        await state.update_data(_state_before_language=current_state)

    await message.answer(
        t(user_lang, "language.choose"),
        reply_markup=language_keyboard()
    )
    await state.set_state(user_states.choosing_language)

async def passenger_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    await message.answer(t(user_lang, "choose.option"), reply_markup=passenger_keyboard(user_lang))
    await state.set_state(user_states.choose_option)

async def travel_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    await message.answer(
        f"{t(user_lang, 'input.name')}\n{t(user_lang, 'edit.example')}: Ali",
        reply_markup=cancel_keyboard_for(user_lang)
    )
    await state.set_state(user_states.user_firstname)

async def process_firstname(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    user_lang = await get_user_lang(message)
    await state.update_data(user_firstname=message.text)
    await message.answer(
        f"{t(user_lang, 'input.surname')}\n{t(user_lang, 'edit.example')}: Valiyev",
        reply_markup=cancel_keyboard_for(user_lang)
    )
    await state.set_state(user_states.user_lastname)


async def process_lastname(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    user_lang = await get_user_lang(message)
    await state.update_data(user_lastname=message.text)
    await message.answer(
        f"{t(user_lang, 'input.phone')}\n{t(user_lang, 'edit.example')}: +998901234567",
        reply_markup=phone_keyboard(user_lang)
    )
    await state.set_state(user_states.user_phone)


async def process_phone(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    await message.answer(t(user_lang, "phone.accepted"), reply_markup=ReplyKeyboardRemove())

    if message.contact and message.contact.phone_number:
        phone = str(message.contact.phone_number)
    else:
        phone = (message.text or "").strip()

    await state.update_data(user_phone=normalize_phone_number(phone) or phone)

    from .keyboards import place_keyboard
    await message.answer(t(user_lang, "input.from"), reply_markup=place_keyboard(user_lang, type="from"))
    await state.set_state(user_states.user_place1)


async def process_location(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    user_lang = await get_user_lang(message)

    if not message.location:
        await message.answer(t(user_lang, "error.location_required"))
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

    await state.update_data(
        user_location=message.location
    )
    await message.answer(
        f"{t(user_lang, 'input.people_count')}\n{t(user_lang, 'edit.example')}: 2, 3, 4",
        reply_markup=cancel_keyboard_for(user_lang)
    )
    await state.set_state(user_states.user_people)

async def show_order_summary(message: Message, state: FSMContext):
    
    data = await state.get_data()
    user_lang = await get_user_lang(message)
    missing_fields = get_missing_order_fields(data)

    if missing_fields:
        await message.answer(
            "Ma'lumotlar to'liq emas. Iltimos, e'lon yaratishni qaytadan boshlang.\n"
            f"Yetishmayotgan ma'lumotlar: {', '.join(missing_fields)}",
            reply_markup=passenger_keyboard(user_lang)
        )
        await state.clear()
        await state.set_state(user_states.choose_option)
        return

    summary = (
        f"{t(user_lang, 'summary.title')}\n\n"
        f"{t(user_lang, 'summary.firstname')}: {data.get('user_firstname')}\n"
        f"{t(user_lang, 'summary.lastname')}: {data.get('user_lastname')}\n"
        f"{t(user_lang, 'summary.phone')}: {data.get('user_phone')}\n"
        f"{t(user_lang, 'summary.from')}: {data.get('user_place1')}\n"
        f"{t(user_lang, 'summary.to')}: {data.get('user_place2')}\n"
        f"{t(user_lang, 'summary.people')}: {data.get('user_people')}\n\n"
    )

    await message.answer(summary, reply_markup=confirm_keyboard(user_lang))
    await state.set_state(user_states.confirm_order)

async def process_people(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    user_lang = await get_user_lang(message)
    people_count = message.text.strip()
    
    if not people_count.isdigit():
        await message.answer(t(user_lang, "error.number_required"))
        return 

    await state.update_data(user_people=int(people_count))
    await show_order_summary(message, state)

async def confirm_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_lang = await get_user_lang(message)
    missing_fields = get_missing_order_fields(data)

    if missing_fields:
        await message.answer(
            "E'lon yuborilmadi, chunki ma'lumotlar to'liq emas.\n"
            f"Yetishmayotgan ma'lumotlar: {', '.join(missing_fields)}\n\n"
            "Iltimos, e'lon yaratishni qaytadan boshlang.",
            reply_markup=passenger_keyboard(user_lang)
        )
        await state.clear()
        await state.set_state(user_states.choose_option)
        return

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
        reply_markup=passenger_keyboard(user_lang)
    )

    await state.set_state(user_states.choose_option)
async def cancel_order(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    
    await message.answer(
        "❌ Buyurtma bekor qilindi.",
        reply_markup=passenger_keyboard(user_lang)
    )

    await state.set_state(user_states.choose_option)

async def show_edit_menu(message: Message, state: FSMContext, user_lang: str | None = None):
    if user_lang is None:
        user_lang = await get_user_lang(message)
    await message.answer(
        t(user_lang, "edit.choose_field"),
        reply_markup=edit_keyboard(user_lang)
    )
    await state.set_state(user_states.edit_field)


async def edit_place_back_message(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state, user_lang)

async def choose_edit_field(message: Message, state: FSMContext):
    if await check_cancel(message, state):
        return
    user_lang = await get_user_lang(message)
    labels = {
        "back": {t(lang, "button.back") for lang in ("uz", "ru", "en")},
        "firstname": {t(lang, "field.firstname") for lang in ("uz", "ru", "en")},
        "lastname": {t(lang, "field.lastname") for lang in ("uz", "ru", "en")},
        "phone": {t(lang, "field.phone") for lang in ("uz", "ru", "en")},
        "place1": {t(lang, "field.from") for lang in ("uz", "ru", "en")},
        "place2": {t(lang, "field.to") for lang in ("uz", "ru", "en")},
        "location": {t(lang, "field.location") for lang in ("uz", "ru", "en")},
        "people": {t(lang, "field.people") for lang in ("uz", "ru", "en")},
    }

    if message.text in labels["back"]:
        await show_order_summary(message, state)
        return
    if message.text in labels["firstname"]:
        await edit_firstname_start(message, state)
    elif message.text in labels["lastname"]:
        await edit_lastname_start(message, state)
    elif message.text in labels["phone"]:
        await edit_phone_start(message, state)
    elif message.text in labels["place1"]:
        await edit_place1_start(message, state)
    elif message.text in labels["place2"]:
        await edit_place2_start(message, state)
    elif message.text in labels["location"]:
        await edit_location_start(message, state)
    elif message.text in labels["people"]:
        await edit_people_start(message, state)
    else:
        await message.answer(t(user_lang, "role.invalid"))

async def _is_back_text(text: str | None) -> bool:
    return text in {t(lang, "button.back") for lang in ("uz", "ru", "en")}


async def edit_firstname_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_name = data.get('user_firstname', '')

    await message.answer(
        f"{t(user_lang, 'edit.firstname')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_name}</b>\n"
        f"{t(user_lang, 'edit.example')}: Ali",
        reply_markup=back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(user_states.editing_firstname)


async def edit_firstname_save(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state)
        return

    new_name = (message.text or '').strip()
    if not new_name:
        await message.answer(t(user_lang, "error.firstname_required"))
        return

    await state.update_data(user_firstname=new_name)
    await show_order_summary(message, state)


async def edit_lastname_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_lastname = data.get('user_lastname', '')

    await message.answer(
        f"{t(user_lang, 'edit.lastname')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_lastname}</b>\n"
        f"{t(user_lang, 'edit.example')}: Valiyev",
        reply_markup=back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(user_states.editing_lastname)


async def edit_lastname_save(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state)
        return

    new_lastname = (message.text or '').strip()
    if not new_lastname:
        await message.answer(t(user_lang, "error.lastname_required"))
        return

    await state.update_data(user_lastname=new_lastname)
    await show_order_summary(message, state)


async def edit_phone_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_phone = data.get('user_phone', '')

    await message.answer(
        f"{t(user_lang, 'edit.phone')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_phone}</b>\n"
        f"{t(user_lang, 'edit.example')}: +998901234567",
        reply_markup=phone_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(user_states.editing_phone)


async def edit_phone_save(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state)
        return

    if message.contact and message.contact.phone_number:
        new_phone = str(message.contact.phone_number)
    else:
        new_phone = (message.text or '').strip()

    normalized_phone = normalize_phone_number(new_phone)
    if not normalized_phone:
        await message.answer(t(user_lang, "error.phone_invalid"))
        return

    await state.update_data(user_phone=normalized_phone)
    await show_order_summary(message, state)


async def edit_place1_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_place = data.get('user_place1', '')

    await message.answer(
        f"{t(user_lang, 'edit.place1')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_place}</b>",
        reply_markup=back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await message.answer(
        t(user_lang, "edit.place1"),
        reply_markup=place_keyboard(user_lang, "from")
    )
    await state.set_state(user_states.editing_place1)


async def edit_place1_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "place_back":
        await callback.message.delete()
        user_lang = await UserService.get_user_language(str(callback.from_user.id))
        await show_edit_menu(callback.message, state, user_lang)
        await callback.answer()
        return

    if data.startswith("place1_"):
        user_lang = await UserService.get_user_language(str(callback.from_user.id))
        place = data.split("_", 1)[1]
        await state.update_data(user_place1=place)
        await callback.message.delete()
        await show_edit_menu(callback.message, state, user_lang)
        await callback.answer()


async def edit_place2_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_place = data.get('user_place2', '')

    await message.answer(
        f"{t(user_lang, 'edit.place2')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_place}</b>",
        reply_markup=back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await message.answer(
        t(user_lang, "edit.place2"),
        reply_markup=place_keyboard(user_lang, "to")
    )
    await state.set_state(user_states.editing_place2)


async def edit_place2_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "place_back":
        await callback.message.delete()
        user_lang = await UserService.get_user_language(str(callback.from_user.id))
        await show_edit_menu(callback.message, state, user_lang)
        await callback.answer()
        return

    if data.startswith("place2_"):
        user_lang = await UserService.get_user_language(str(callback.from_user.id))
        place = data.split("_", 1)[1]
        await state.update_data(user_place2=place)
        await callback.message.delete()
        await show_edit_menu(callback.message, state, user_lang)
        await callback.answer()


async def edit_location_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_location = data.get('user_location')
    location_text = t(user_lang, "location.exists") if current_location else t(user_lang, "location.missing")

    await message.answer(
        f"{t(user_lang, 'edit.location')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{location_text}</b>",
        reply_markup=location_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(user_states.editing_location)


async def edit_location_save(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state)
        return

    if not message.location:
        await message.answer(t(user_lang, "error.location_required"))
        return

    await state.update_data(user_location=message.location)
    await show_order_summary(message, state)


async def edit_people_start(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    data = await state.get_data()
    current_people = data.get('user_people', '')

    await message.answer(
        f"{t(user_lang, 'edit.people')}\n\n"
        f"{t(user_lang, 'edit.current')}: <b>{current_people}</b>\n"
        f"{t(user_lang, 'edit.example')}: 2, 3, 4",
        reply_markup=back_keyboard(user_lang),
        parse_mode="HTML"
    )
    await state.set_state(user_states.editing_people)


async def edit_people_save(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    if await _is_back_text(message.text):
        await show_edit_menu(message, state)
        return

    people_count = (message.text or '').strip()
    if not people_count.isdigit():
        await message.answer(t(user_lang, "error.number_required"))
        return

    await state.update_data(user_people=int(people_count))
    await show_order_summary(message, state)



async def send_order_to_channel(bot: Bot, state: FSMContext, order_id, user_id):
    data = await state.get_data()
    user_lang = await UserService.get_user_language(str(user_id))
    
    location = data.get("user_location")
    
    map_link = ""
    if location:
        map_link = f"https://maps.google.com/?q={location.latitude},{location.longitude}"

    text = f"""
            🚕 YANGI BUYURTMA #{order_id}

            👤 Ism: {data.get('user_firstname')}
            👤 Familiya: {data.get('user_lastname')}
            📞 Telefon: {data.get('user_phone')}
    
            📍 Qayerdan: {data.get('user_place1')}
            📍 Qayerga: {data.get('user_place2')}

            👥 Odamlar: {data.get('user_people')}
            📍 Lokatsiya:
            {map_link}
            """

    msg = await bot.send_message(
        CHANNEL_ID,
        text,
        reply_markup=receive(order_id, user_id, user_lang)  
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
    user_lang = await get_user_lang(message)
    link = "https://t.me/taxi_test_uz"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(user_lang, "passenger.channel"), url=link)]
        ]
    )

    await message.answer(
        f"{t(user_lang, 'channel.link')}\n{link}",
        reply_markup=keyboard
    )

async def complaints_start(message, state):
    user_lang = await get_user_lang(message)
    await state.clear()

    await message.answer(
        t(user_lang, "complaint.prompt"),
        reply_markup=back_keyboard(user_lang)
    )

    await state.set_state(user_states.complaint_text)

async def complaints_handler(message : Message, state : FSMContext, bot):
    user_lang = await get_user_lang(message)

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
    await message.answer(t(user_lang, "complaint.accepted"), reply_markup=back_keyboard(user_lang))
    

async def back_to_choose_option(message : Message, state : FSMContext):
    await state.clear()

    user_lang = await get_user_lang(message)
    await message.answer(t(user_lang, "back.to_menu"), reply_markup=passenger_keyboard(user_lang))

    await state.set_state(user_states.choose_option)

async def check_cancel(message: Message, state: FSMContext):
    user_lang = await get_user_lang(message)
    cancel_labels = {t(lang, "button.cancel") for lang in ("uz", "ru", "en")}
    if message.text in cancel_labels:
        await state.clear()
        await message.answer(
            t(user_lang, "order.cancelled"),
            reply_markup=passenger_keyboard(user_lang)
        )
        await state.set_state(user_states.choose_option)
        return True
    return False
