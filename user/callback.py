# Here you need write your callbacks
from aiogram.types import CallbackQuery
from user.i18n import t
from aiogram.fsm.context import FSMContext
from .states import user_states
from .keyboards import place_keyboard

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
        "5️⃣ Qayerga borasiz?",
        reply_markup=place_keyboard("uz", type="to")
    )

    await call.answer()
# ======================
# Qayerga 
async def process_place2(call: CallbackQuery, state: FSMContext):
    place2 = call.data.split("_")[1]
    data = await state.get_data()
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
        "6️⃣ Iltimos lokatsiyangizni tashlang:"
    )
    await call.answer()

