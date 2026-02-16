# Taksi ma'lumotlari bo'limi (Taxi Info Section)

from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
import sys
import os

# Import CRUD functions
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.crud_commands import (
    create,
    update,
    delete
)
from data.models import Taxi, Complaint, session


# ===== STATES =====
class taxi_info_states(StatesGroup):
    update_firstname = State()
    update_lastname = State()
    update_car_model = State()
    update_car_number = State()
    complaint_info = State()



async def show_taxi_info(message: Message, state: FSMContext):
    """Taksi ma'lumotlarini ko'rsatish"""
    telegram_id = message.from_user.id
    
    # Taksi ma'lumotlarini olish
    taxi = session.query(Taxi).filter_by(telegram_id=telegram_id).first()
    
    if not taxi:
        await message.answer("❌ Siz ro'yxatdan o'tmagan yoki ma'lumotlaringiz topilmadi!")
        return
    
    # Taksi ma'lumotlarini chiqarish
    info_text = f"""
📋 <b>Sizning taksi ma'lumotlaringiz:</b>

👤 <b>Ism:</b> {taxi.fullname}
📱 <b>Nomer:</b> {taxi.nomer}
🚗 <b>Avtomobil modeli:</b> {taxi.car_model}
🔢 <b>Avtomobil raqami:</b> {taxi.car_nomer}
🆔 <b>Telegram ID:</b> {taxi.telegram_id}
    """
    
    await message.answer(info_text, parse_mode="HTML")


async def get_updated_firstname(message: Message, state: FSMContext):
    """Yangilangan isimni qabul qilish"""
    await state.update_data(updated_firstname=message.text)
    await message.answer("Yangilangan familiyangizni kiriting:")
    await state.set_state(taxi_info_states.update_lastname)


async def get_updated_lastname(message: Message, state: FSMContext):
    """Yangilangan familiyani qabul qilish"""
    data = await state.get_data()
    firstname = data.get("updated_firstname")
    
    await state.update_data(updated_lastname=message.text)
    await message.answer("Yangilangan avtomobil modelini kiriting:")
    await state.set_state(taxi_info_states.update_car_model)


async def get_updated_car_model(message: Message, state: FSMContext):
    """Yangilangan avtomobil modelini qabul qilish"""
    data = await state.get_data()
    
    await state.update_data(updated_car_model=message.text)
    await message.answer("Yangilangan avtomobil raqamini kiriting:")
    await state.set_state(taxi_info_states.update_car_number)


async def get_updated_car_number(message: Message, state: FSMContext):
    """Yangilangan avtomobil raqamini qabul qilish va saqlash"""
    data = await state.get_data()
    telegram_id = message.from_user.id
    
    updated_firstname = data.get("updated_firstname")
    updated_lastname = data.get("updated_lastname")
    updated_car_model = data.get("updated_car_model")
    updated_car_number = message.text
    
    # Ma'lumotlarni yangilash
    update(
        Taxi,
        {'telegram_id': telegram_id},
        {
            'fullname': f"{updated_firstname} {updated_lastname}",
            'car_model': updated_car_model,
            'car_nomer': updated_car_number
        }
    )
    
    await message.answer(
        "✅ Sizning ma'lumotlaringiz muvaffaqiyatli yangilandi!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


async def handle_complaint(message: Message, state: FSMContext):
    """Shikoyatni qabul qilish va saqlash"""
    complaint_text = message.text
    
    # Shikoyatni bazaga saqlash
    complaint = create(Complaint, info=complaint_text)
    
    await message.answer(
        "✅ Sizning shikoyatingiz qabul qilindi! Tez orada qarab ko'riladi.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


async def get_taxi_stats(message: Message):
    """Taksi statistikasini ko'rsatish"""
    telegram_id = message.from_user.id
    taxi = session.query(Taxi).filter_by(telegram_id=telegram_id).first()
    
    if not taxi:
        await message.answer("❌ Ma'lumotlar topilmadi!")
        return
    
    stats_text = f"""
📊 <b>Taksi statistikasi:</b>

👤 Ism familiya: {taxi.fullname}
📊 Reytingi: ⭐⭐⭐⭐⭐ (5.0)
🚗 Tariflar: 5,000 so'm/km
📈 Jami sayohatlar: 150
📅 Ro'yxatga olingan: 2024-01-15
    """
    
    await message.answer(stats_text, parse_mode="HTML")


async def update_taxi_profile(message: Message, state: FSMContext):
    """Taksi profilini yangilash uchun boshlang'ich funksiya"""
    await message.answer(
        "📝 Profil yangilash uchun yangi isimingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(taxi_info_states.update_firstname)
