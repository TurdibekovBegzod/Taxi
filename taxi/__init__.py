from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from user.i18n import t

from .filters import PhoneFilter
from .functions import (
    back_to_edit_confirm,
    back_to_profile,
    change_role_command_answer,
    choose_edit_car_model,
    choose_edit_car_number,
    choose_edit_firstname,
    choose_edit_lastname,
    choose_edit_phone,
    complaints_handler,
    complaints_start,
    confirm_answer,
    get_car_model_answer,
    get_car_number_answer,
    get_contact_answer,
    get_firstname_answer,
    get_lastname_answer,
    get_new_car_model_answer,
    get_new_car_number_answer,
    get_new_firstname_answer,
    get_new_lastname_answer,
    get_new_phone_answer,
    info_answer,
    sign_up_answer,
    start_command_answer,
    to_choose_a_role_answer,
    update_info_answer,
)
from .states import taxi_states

router = Router()

SIGN_UP_BUTTONS = {t(lang, "button.sign_up") for lang in ("uz", "ru", "en")}
CONFIRM_BUTTONS = {t(lang, "button.confirm") for lang in ("uz", "ru", "en")}
COMPLAINT_BUTTONS = {t(lang, "passenger.complaints") for lang in ("uz", "ru", "en")}
BACK_BUTTONS = {t(lang, "button.back") for lang in ("uz", "ru", "en")}
INFO_BUTTONS = {t(lang, "taxi.button.info") for lang in ("uz", "ru", "en")}
EDIT_INFO_BUTTONS = {t(lang, "taxi.button.edit_info") for lang in ("uz", "ru", "en")}
FIRSTNAME_BUTTONS = {t(lang, "field.firstname") for lang in ("uz", "ru", "en")}
LASTNAME_BUTTONS = {t(lang, "field.lastname") for lang in ("uz", "ru", "en")}
PHONE_BUTTONS = {t(lang, "field.phone") for lang in ("uz", "ru", "en")}
CAR_MODEL_BUTTONS = {t(lang, "field.car_model") for lang in ("uz", "ru", "en")}
CAR_NUMBER_BUTTONS = {t(lang, "field.car_number") for lang in ("uz", "ru", "en")}

router.message.register(start_command_answer, CommandStart())
router.message.register(change_role_command_answer, Command("change_role"))
router.message.register(to_choose_a_role_answer, taxi_states.choosing_role)

router.message.register(sign_up_answer, F.text.in_(SIGN_UP_BUTTONS))
router.message.register(get_firstname_answer, taxi_states.firstname)
router.message.register(get_lastname_answer, taxi_states.lastname)
router.message.register(get_contact_answer, taxi_states.contact, PhoneFilter())
router.message.register(get_car_model_answer, taxi_states.car_model)
router.message.register(get_car_number_answer, taxi_states.car_number)
router.message.register(confirm_answer, taxi_states.confirm, F.text.in_(CONFIRM_BUTTONS))

router.message.register(complaints_start, taxi_states.profile, F.text.in_(COMPLAINT_BUTTONS))
router.message.register(back_to_profile, taxi_states.complaint_text, F.text.in_(BACK_BUTTONS))
router.message.register(complaints_handler, taxi_states.complaint_text)

router.message.register(info_answer, taxi_states.profile, F.text.in_(INFO_BUTTONS))
router.message.register(update_info_answer, taxi_states.profile, F.text.in_(EDIT_INFO_BUTTONS))
router.message.register(choose_edit_firstname, taxi_states.edit_confirm, F.text.in_(FIRSTNAME_BUTTONS))
router.message.register(back_to_edit_confirm, taxi_states.edit_firstname, F.text.in_(BACK_BUTTONS))
router.message.register(choose_edit_lastname, taxi_states.edit_confirm, F.text.in_(LASTNAME_BUTTONS))
router.message.register(back_to_edit_confirm, taxi_states.edit_lastname, F.text.in_(BACK_BUTTONS))
router.message.register(choose_edit_phone, taxi_states.edit_confirm, F.text.in_(PHONE_BUTTONS))
router.message.register(back_to_edit_confirm, taxi_states.edit_phone, F.text.in_(BACK_BUTTONS))
router.message.register(choose_edit_car_model, taxi_states.edit_confirm, F.text.in_(CAR_MODEL_BUTTONS))
router.message.register(back_to_edit_confirm, taxi_states.edit_car_model, F.text.in_(BACK_BUTTONS))
router.message.register(choose_edit_car_number, taxi_states.edit_confirm, F.text.in_(CAR_NUMBER_BUTTONS))
router.message.register(back_to_edit_confirm, taxi_states.edit_car_number, F.text.in_(BACK_BUTTONS))
router.message.register(back_to_profile, taxi_states.edit_confirm, F.text.in_(BACK_BUTTONS))

router.message.register(get_new_firstname_answer, taxi_states.edit_firstname)
router.message.register(get_new_lastname_answer, taxi_states.edit_lastname)
router.message.register(get_new_phone_answer, taxi_states.edit_phone, PhoneFilter())
router.message.register(get_new_car_model_answer, taxi_states.edit_car_model)
router.message.register(get_new_car_number_answer, taxi_states.edit_car_number)

__all__ = ["router"]
