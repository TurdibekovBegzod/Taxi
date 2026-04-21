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
    user_people = State()
    user_confirm = State()
    confirm_order = State() #
    edit_field = State()
    edit= State()
    editing_firstname = State()
    editing_lastname = State()
    editing_phone = State()
    editing_place1 = State()
    editing_place2 = State()
    editing_location = State()
    editing_people = State()

    complaint_text = State()
