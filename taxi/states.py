from aiogram.fsm.state import StatesGroup, State

class taxi_states(StatesGroup):
    profile = State()
    choosing_role = State()
    firstname = State()
    lastname = State()
    contact = State()
    car_model = State()
    car_number = State()
    confirm = State()
    complaint_text = State()

    edit_firstname = State()
    edit_lastname = State()
    edit_phone = State()
    edit_car_model = State()
    edit_car_number = State()
    edit_confirm = State()