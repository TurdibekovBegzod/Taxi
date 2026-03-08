from aiogram import Router, F
from .functions import (
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
                        get_new_firstname_answer,
                        get_new_lastname_answer,
                        get_new_phone_answer,
                        get_new_car_model_answer,
                        get_new_car_number_answer,
                        confirm_edit_answer)
from aiogram.filters import CommandStart, Command
from .states import taxi_states


router = Router()

# Here you can connect your functions


router.message.register(start_command_answer, CommandStart())
router.message.register(change_role_command_answer, Command("change_role"))
router.message.register(to_choose_a_role_answer, taxi_states.choosing_role)
router.message.register(sign_up_answer, F.text == "Sign up")
router.message.register(get_firstname_answer, taxi_states.firstname)
router.message.register(get_lastname_answer, taxi_states.lastname)
router.message.register(get_contact_answer, taxi_states.contact)
router.message.register(get_car_model_answer, taxi_states.car_model)
router.message.register(get_car_number_answer, taxi_states.car_number)
router.message.register(confirm_answer, taxi_states.confirm, F.text == "Confirm")

# show info and update handlers
router.message.register(info_answer, F.text == "Info")
router.message.register(update_info_answer, F.text == "Update info")
# edit sequence handlers
router.message.register(get_new_firstname_answer, taxi_states.edit_firstname)
router.message.register(get_new_lastname_answer, taxi_states.edit_lastname)
router.message.register(get_new_phone_answer, taxi_states.edit_phone)
router.message.register(get_new_car_model_answer, taxi_states.edit_car_model)
router.message.register(get_new_car_number_answer, taxi_states.edit_car_number)
router.message.register(confirm_edit_answer, taxi_states.edit_confirm, F.text == "Confirm")

# example to connect functions
# router.message.register(function_name, filters, commands)
