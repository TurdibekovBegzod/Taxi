# Here you need to write your states

from aiogram.fsm.state import StatesGroup, State


class user_states(StatesGroup):
    choosing_language = State()
    choose_option = State()
    user_firstname = State()
    user_lastname = State()
    user_phone = State()
    user_place1 = State()
    user_place2 = State()
    user_location = State()   #
    # user_time = State()
    user_people = State()
    user_confirm = State()

    confirm_order = State() #
    edit_field = State()
    edit_value = State()

    complaint_text = State()
