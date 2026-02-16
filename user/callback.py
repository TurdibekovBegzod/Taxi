# Here you need write your callbacks
from aiogram.types import CallbackQuery
from user.i18n import t
async def language_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[1]  # uz yoki ru

    # Bu yerda keyin FSM yoki DB ga saqlaysiz

    await callback.message.edit_text(
        t(lang, f"language.changed.{lang}")
    )
    await callback.answer()
    


from aiogram.fsm.context import FSMContext
from .states import user_states
from .keyboards import place_keyboard

# ======================
# Qayerdan tugma callback
async def process_place1(call: CallbackQuery, state: FSMContext):
    place1 = call.data.split("_")[1]  # call.data = "place1_Toshkent"
    await state.update_data(user_place1=place1)
    await state.set_state(user_states.user_place2)
    await call.message.answer(
        "5️⃣ Qayerga borasiz?",
        reply_markup=place_keyboard("uz", type="to")  # bitta funksiya Qayerga uchun ishlatiladi
    )
    await call.answer()

# ======================
# Qayerga tugma callback
async def process_place2(call: CallbackQuery, state: FSMContext):
    place2 = call.data.split("_")[1]  # call.data = "place2_Xorazm"
    await state.update_data(user_place2=place2)
    await state.set_state(user_states.user_confirm)
    await call.message.answer("6️⃣ Iltimos lokatsiyangizni tashlang:", reply_markup=None)
    await call.answer()
