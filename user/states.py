# Here you need to write your states

from aiogram.fsm.state import StatesGroup, State


class taxi_states(StatesGroup):
    choosing_role = State()
    firstname = State()
    lastname = State()
    contact = State()
    car_model = State()
    car_number = State()
    confirm = State()