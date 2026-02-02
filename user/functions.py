# Here you need write your functions
from aiogram.types import Message
from aiogram import Bot
from .keyboards import (
                        show_role_buttons, 
                        sign_up,
                        get_contact,
                        confirm)

from aiogram.fsm.context import FSMContext
from .states import taxi_states
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove


async def start_command_answer(message : Message, bot : Bot, state : FSMContext):
    await message.answer(text = "Welcome to our bot, user!")
    await message.answer(text = "Choose your role!", reply_markup=show_role_buttons)
    await state.clear() # clear the state
    await state.set_state(taxi_states.choosing_role) # turn on the <choosing_role> state in taxi_states

async def change_role_command_answer(message : Message, state : FSMContext):
    await state.clear()
    await message.answer(text = "Choose your role!", reply_markup=show_role_buttons)
    await state.set_state(taxi_states.choosing_role) # turn on the <choosing_role> state in taxi_states


async def to_choose_a_role_answer(message : Message, state : FSMContext):
    if not(message.text == "Passenger" or message.text == "Driver"):
        await message.answer("You need to choose your role matched on the keyboard!")
        return
    
    if not taxi_states.choosing_role:
        return
    
    await message.answer(text = f"Your role is {message.text}!")

    if message.text == "Driver":
        """
        I need to write code to check the taxi driver is available in our database!
        """

        await message.answer(text = """Driver, you're not registered yet!
                             \nPlease sign up!""",
                             reply_markup=sign_up)

    await state.update_data(role = message.text)
    await state.set_state(None) # turn off the state

async def sign_up_answer(message : Message, state : FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer(text = "Your're not right place !")
        return
    await message.answer(text = "Please enter your firstname!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(taxi_states.firstname)

async def get_firstname_answer(message : Message, state : FSMContext):
    await message.answer(f"Your name is {message.text}")
    await message.answer("Please enter your lastname!")
    await state.update_data(firstname = message.text)
    await state.set_state(taxi_states.lastname)

async def get_lastname_answer(message : Message, state : FSMContext):
    await message.answer(f"Your lastname is {message.text}")
    await message.answer("Please send your contact!", reply_markup=get_contact)
    await state.set_state(taxi_states.contact)

async def get_contact_answer(message : Message, state : FSMContext):
    await message.answer("Your contact is taked!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Please enter your car model!")
    await state.update_data(phone_number = str(message.contact.phone_number))
    await state.set_state(taxi_states.car_model)

async def get_car_model_answer(message : Message, state : FSMContext):
    await message.answer(f"Your car model is {message.text}")
    await message.answer("Please enter you car number!")
    await state.update_data(car_model = message.text)
    await state.set_state(taxi_states.car_number)

async def get_car_number_answer(message : Message, state : FSMContext):
    await message.answer(f"Your car number is {message.text}!")
    await state.update_data(car_number = message.text)
    await message.answer("""Please make sure your all information is right, and confirm!""", reply_markup=confirm)
    await state.set_state(taxi_states.confirm)

async def confirm_answer(message : Message, state : FSMContext):
    data = await state.get_data()

    await message.answer(f"{data}")
    """
    I need to write code to save all information about a taxi driver using database.
    """

    await message.answer("Your all information is saved ✅!")
    await state.clear()






        
