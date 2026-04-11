from aiogram import Router, F
from .functions import (
    complaints_start,
    start_command_answer,
    to_choose_a_role_answer,
    sign_up_answer,
    get_firstname_answer,
    get_lastname_answer,
    get_contact_answer,
    get_car_model_answer,
    get_car_number_answer,
    confirm_answer,
    change_role_command_answer,
    info_answer,
    update_info_answer,
    choose_edit_firstname,
    choose_edit_lastname,
    choose_edit_phone,
    choose_edit_car_model,
    choose_edit_car_number,
    back_to_profile,
    get_new_firstname_answer,
    get_new_lastname_answer,
    get_new_phone_answer,
    get_new_car_model_answer,
    get_new_car_number_answer,
    back_to_edit_confirm,
    complaints_handler
)
from .filters import PhoneFilter
from aiogram.filters import CommandStart, Command
from .states import taxi_states

router = Router()

router.message.register(start_command_answer, CommandStart())
router.message.register(change_role_command_answer, Command("change_role"))
router.message.register(to_choose_a_role_answer, taxi_states.choosing_role)

router.message.register(sign_up_answer, F.text == "Ro‘yxatdan o‘tish")
router.message.register(get_firstname_answer, taxi_states.firstname)
router.message.register(get_lastname_answer, taxi_states.lastname)
router.message.register(get_contact_answer, taxi_states.contact, PhoneFilter())
router.message.register(get_car_model_answer, taxi_states.car_model)
router.message.register(get_car_number_answer, taxi_states.car_number)
router.message.register(confirm_answer, taxi_states.confirm, F.text == "Tasdiqlash")

router.message.register(complaints_start,taxi_states.profile, F.text == "Shikoyatlar va takliflar")
router.message.register(back_to_profile, taxi_states.complaint_text, F.text == "◀️ Orqaga")
router.message.register(complaints_handler, taxi_states.complaint_text)

router.message.register(info_answer, taxi_states.profile, F.text == "📄 Ma'lumot")
router.message.register(update_info_answer, taxi_states.profile, F.text == "📝 Ma'lumotlarni o'zgartirish")
router.message.register(choose_edit_firstname, taxi_states.edit_confirm, F.text == "Ism")
router.message.register(back_to_edit_confirm, taxi_states.edit_firstname, F.text == "◀️ Orqaga")
router.message.register(choose_edit_lastname, taxi_states.edit_confirm, F.text == "Familiya")
router.message.register(back_to_edit_confirm, taxi_states.edit_lastname, F.text == "◀️ Orqaga")
router.message.register(choose_edit_phone, taxi_states.edit_confirm, F.text == "Telefon")
router.message.register(back_to_edit_confirm, taxi_states.edit_phone, F.text == "◀️ Orqaga")
router.message.register(choose_edit_car_model, taxi_states.edit_confirm, F.text == "Mashina modeli")
router.message.register(back_to_edit_confirm, taxi_states.edit_car_model, F.text == "◀️ Orqaga")
router.message.register(choose_edit_car_number, taxi_states.edit_confirm, F.text == "Mashina raqami")
router.message.register(back_to_edit_confirm, taxi_states.edit_car_number, F.text == "◀️ Orqaga")
router.message.register(back_to_profile, taxi_states.edit_confirm, F.text == "◀️ Orqaga")

router.message.register(get_new_firstname_answer, taxi_states.edit_firstname)
router.message.register(get_new_lastname_answer, taxi_states.edit_lastname)
router.message.register(get_new_phone_answer, taxi_states.edit_phone, PhoneFilter())
router.message.register(get_new_car_model_answer, taxi_states.edit_car_model)
router.message.register(get_new_car_number_answer, taxi_states.edit_car_number)

__all__ = ['router']