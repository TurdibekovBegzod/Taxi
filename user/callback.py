# Here you need write your callbacks
from aiogram.types import CallbackQuery
from user.i18n import t
from aiogram.fsm.context import FSMContext
from .states import user_states
from .keyboards import btn_location_keyboard, place_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.models import Order
import uuid
from datetime import datetime, timedelta, timezone
from user.my_scheduler import scheduler
from user.keyboards import receive

from data.driver_check import is_driver, get_driver
from data.crud_commands import get, delete_order, get_order, update
from data.models import User



async def language_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[1]  # uz yoki ru

    # Bu yerda keyin FSM yoki DB ga saqlaysiz

    await callback.message.edit_text(
        t(lang, f"language.changed.{lang}")
    )
    await callback.answer()
    
# ======================
# Qayerdan 
async def process_place1(call: CallbackQuery, state: FSMContext):
    place1 = call.data.split("_")[1]
    data = await state.get_data()

    if data.get('user_place2'):
        if data['user_place2'] == place1:
            await call.answer("❌ Manzillar bir xil bo'lishi mumkin emas!", show_alert=True)
            
            return
        
    
    await state.update_data(user_place1=place1)

    # tahrirlash bo'lsa
    if data.get("editing_field") == "user_from":
        from .functions import show_order_summary
        await show_order_summary(call.message, state)
        await call.answer()
        return

    # bo'yurtma yaratishda
    await state.set_state(user_states.user_place2)
    await call.message.answer(
        "Qayerga borasiz?",
        reply_markup=place_keyboard("uz", type="to")
    )

    await call.answer()
# ======================
# Qayerga 
async def process_place2(call: CallbackQuery, state: FSMContext):
    place2 = call.data.split("_")[1]
    data = await state.get_data()
    if data['user_place1'] == place2:
        await call.answer("❌ Manzillar bir xil bo'lishi mumkin emas!", show_alert=True)
        
        return  
    await state.update_data(user_place2=place2)

    # tahrirlash
    if data.get("editing_field") == "user_to":
        from .functions import show_order_summary
        await show_order_summary(call.message, state)
        await call.answer()
        return

    # bo'yurtma yaratisda
    await state.set_state(user_states.user_confirm)

    await call.message.answer(
        "Iltimos lokatsiyangizni tashlang 📍:"
        ,
        reply_markup=btn_location_keyboard
    )
    await call.answer()

# Bog'lanish va Qabul qilish


async def accept_order(callback: CallbackQuery):
    driver = await get_driver(int(callback.from_user.id))
    order_id_side = callback.data.split("|", 1)[0]
    user_id_side = callback.data.split("|", 1)[1]
    order_id = order_id_side.replace("accept_", "")
    user_id = user_id_side.replace("uid_", "")
    order_id_str = str(order_id)

    # Faqat haydovchi tekshiruvi
    if not await is_driver(int(callback.from_user.id)):
        await callback.answer("❌ Bu tugmani faqat haydovchilar bosishi mumkin!", show_alert=True)
        return callback.from_user.id
    
    if str(driver.telegram_id) == user_id:
        await callback.answer("❌ Siz o'zingiz yaratgan buyurtmani qabul qila olmaysiz!", show_alert=True)
        return callback.from_user.id


    order = await get(Order, {"uid": order_id})

    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    await update(Order, {"uid": order_id}, {
        "driver_id": driver.telegram_id,
        "chat_id": callback.message.chat.id,
        "status": "accepted",
        "resent": 0
})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Telegramda yozish",
                url=f"tg://user?id={user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Buyurtmani tasdiqlash",
                callback_data=f"confirm_{order_id_str}"
            )
        ]
    ])

    # 🔥 Haydovchiga yuborish (faqat bog‘lanish tugmasi bilan)
    await callback.bot.send_message(
        chat_id=driver.telegram_id,
        text=(
            f"🚖 Siz buyurtmani qabul qildingiz!\n\n"
            f"{callback.message.text}\n\n"
            f" Yo'lovchi bilan bog'langaningizdan keyin Buyurtmani tasdiqlash tugmasini bosing"
        ),
        reply_markup=keyboard
    )
    # ====== YO‘LOVCHIGA XABAR ======
    await callback.bot.send_message(
        chat_id=user_id,

        text=(
            "🚕 Sizning so'rovingiz taxi tomonidan ko'rib chiqilmoqda\n\n"
            f"👤 Taxi: {driver.firstname} {driver.lastname}\n"
            f"📞 Telefon: {driver.phone_number}"
        )
    )


    # ====== LOKATSIYANI O‘CHIRISH ======
    order = await get(Order, {"uid": order_id})

    if order.location_message_id:
        await callback.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=order.location_message_id
    )


    # ====== TEXT XABARNI O‘CHIRISH ======
    try:
        await callback.message.delete()
        print("Text o‘chirildi")
    except Exception as e:
        print("Text xatosi:", e)



    # ====== 40 sekunddan keyin eslatma ======
    
    ask_request_time = datetime.now(timezone.utc) + timedelta(minutes = 5)
    send_request_time = datetime.now(timezone.utc) + timedelta(minutes = 20)

    scheduler.add_job(
        send_followup_wrapper,
        trigger="date",
        run_date=ask_request_time,
        kwargs={
            "bot": callback.bot,
            "order_id": order_id_str
        },
        id=f"followup_{order_id_str}",
        replace_existing=True
    )
    scheduler.add_job(
        send_request,
        trigger="date",
        run_date=send_request_time,
        kwargs={
            "bot": callback.bot,
            "order_id": order_id_str
        }
    )


    await callback.answer("✅ Buyurtma qabul qilindi!")


async def contact_passenger(callback: CallbackQuery):
    if not await is_driver(str(callback.from_user.id)):
        await callback.answer("❌ Bu tugmani faqat haydovchilar bosishi mumkin!", show_alert=True)
        return
    
    
    order_id = uuid.UUID(callback.data.split("_", 1)[1])

    order = await get(Order, {"uid": order_id})

    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    passenger_id = order.user_id


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Telegramda yozish",
                url=f"tg://user?id={passenger_id}"
            )
        ]
    ])

    text = "📞 Yo‘lovchi bilan bog‘lanish uchun tugmani bosing."

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=keyboard
    )

    await callback.answer("✅ Sizga shaxsiy xabar yuborildi.", show_alert=True)



# ======================== TASDIQLASH FUNKSIYASI======================

async def confirm_order(callback: CallbackQuery):

    order_id = callback.data.split("_")[1]

    order = await get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi", show_alert=True)
        return

    passenger_id = order["passenger_id"]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ha",
                    callback_data=f"client_yes_{order_id}"
                ),
                InlineKeyboardButton(
                    text="Yo'q",
                    callback_data=f"client_no_{order_id}"
                )
            ]
        ]
    )

    await callback.bot.send_message(
        chat_id=passenger_id,
        text="🚕 Taxi siz bilan bog'landimi?",
        reply_markup=keyboard
    )

    await callback.answer("So'rov yuborildi ✅")

# YO‘LOVCHI HA BOSSA
async def client_yes(callback: CallbackQuery):
    order_uid_str : str = callback.data.split("_")[2]
    order_uid = uuid.UUID(order_uid_str)
    await callback.message.edit_text(
        "😊 Bundan xursandmiz!\n\nYaxshi yo'l tilaymiz 🚕"
    )
    await update(Order, {"uid": order_uid}, {
        "status": "completed"
    })

    await callback.answer()

# YO‘LOVCHI YO‘Q BOSSA
async def client_no(callback: CallbackQuery):

    order_id = callback.data.split("_")[2]

    order = await get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi", show_alert=True)
        return

    driver_id = order["driver_id"]

    await callback.bot.send_message(
        chat_id=driver_id,
        text=(
            "⚠️ Siz hali yo'lovchi bilan bog'lanmagansiz!\n\n"
            "Iltimos yo'lovchi bilan bog'laning."
        )
    )

    await callback.message.edit_text(
        "❗ Taxi hali siz bilan bog'lanmadi."
    )

    await callback.answer()






# 10 mindan keyin tekshrish




async def send_followup_questions(bot, order_id: str):
    order = await get_order(order_id)
    if not order:
        return

    driver_id = order["driver_id"]

    driver_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ha", callback_data=f"driver_yes_{order_id}"),
            InlineKeyboardButton(text="Yo'q", callback_data=f"driver_no_{order_id}")
        ]
    ])

    await bot.send_message(
        chat_id=driver_id,
        text="Yo‘lovchi bilan bog'lana oldingizmi?",
        reply_markup=driver_keyboard
    )

async def send_followup_wrapper(bot, order_id):
    print("JOB ISHLADI:", order_id)
    await send_followup_questions(bot, order_id)

async def send_request(bot, order_id):
    await resend_order_to_group(bot, order_id)


async def resend_order_to_group(bot, order_id: str):
    order = await get_order(order_id)

    text = order.message

    if order.lat and order.lon:
        await bot.send_location(
            chat_id=order.chat_id,
            latitude=order.lat,
            longitude=order.lon
    )

    if not text:
        return
    
    order = await get_order(order_id)
    if not order:
        print("Buyurtma topilmadi DB da:", order_id)
        return
    user_id = order.user_id

    # ✅ 1. TEXT yuboramiz
    msg = await bot.send_message(
        chat_id=order.chat_id,
        text=text,
        reply_markup=receive(order_id, user_id)
    )

    # ✅ 2. AGAR LOCATION BO‘LSA yuboramiz
    order = await get_order(order_id)

    text = order.message

    if order.lat and order.lon:
        await bot.send_location(
            chat_id=order.chat_id,
            latitude=order.lat,
            longitude=order.lon
    )
    # location = order_locations.get(order_id)

    # if location:
    #     lat, lon = location
    #     loc_msg = await bot.send_location(
    #         chat_id=chat_id,
    #         latitude=lat,
    #         longitude=lon
    #     )

    #     # yana mappingni yangilaymiz
    #     location_messages[order_id] = loc_msg.message_id

    # # ✅ BELGI
    # data["resent"] = True



# =============TAXI javoblari===============
# HA==========
async def driver_yes(callback: CallbackQuery):
    order_id = callback.data.replace("driver_yes_", "")

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "😊 Kelishuvingiz muvaffaqiyatli bo‘lganidan xursandmiz."
    )

    # endi userga savol yuboramiz
    order = await get_order(order_id)
    passenger_id = order["passenger_id"]

    passenger_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ha", callback_data=f"passenger_yes_{order_id}"),
            InlineKeyboardButton(text="Yo'q", callback_data=f"passenger_no_{order_id}")
        ]
    ])

    await callback.bot.send_message(
        chat_id=passenger_id,
        text="Taxi bilan bog'lana oldingizmi?",
        reply_markup=passenger_keyboard
    )

    await callback.answer("✅ Javob qabul qilindi")

# ==============YO'Q================

async def driver_no(callback: CallbackQuery):
    order_id = callback.data.replace("driver_no_", "")

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "❌ Kelisha olmaganingizdan afsusdamiz. Buyurtma bekor qilinadi."
    )

    order = await get_order(order_id)
    passenger_id = order["passenger_id"]

    # userga xabar
    await callback.bot.send_message(
        chat_id=passenger_id,
        text="🚕 Taxi siz bilan kelisha olmadi. So‘rovingiz guruhga qayta yuborildi."
    )

    # guruhga qayta yuborish
    await resend_order_to_group(callback.bot, order_id)

    await update(Order, {"uid": order_id}, {
        "status": "cancelled"
    })

    await callback.answer("✅ Javob qabul qilindi")

# ========================USER javoblari=============
# HA================
async def passenger_yes(callback: CallbackQuery):
    order_id = callback.data.replace("passenger_yes_", "")

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "🎉 Kelisha olganingizdan xursandmiz!"
    )

    await update(Order, {"uid": order_id}, {
        "status": "cancelled"
    })

    await callback.answer("✅ Javob qabul qilindi")


#  ========YO'Q======================

async def passenger_no(callback: CallbackQuery):
    order_id = callback.data.replace("passenger_no_", "")

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "❌ Kelisha olmaganingizdan afsusdamiz. So‘rovingiz qayta guruhga yuboriladi."
    )

    order = await get_order(order_id)
    driver_id = order["driver_id"]

    # taxiga xabar
    await callback.bot.send_message(
        chat_id=driver_id,
        text="🚫 Yo‘lovchi buyurtmani bekor qildi."
    )

    # guruhga qayta yuborish
    await resend_order_to_group(callback.bot, order_id)

    await update(Order, {"uid": order_id}, {
        "status": "cancelled"
    })

    await callback.answer("✅ Javob qabul qilindi")
 
