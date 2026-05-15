from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from taxi.keyboards import (
    contact_keyboard,
    edit_profile_keyboard,
    role_keyboard,
    taxi_back_and_phone_keyboard,
    taxi_back_keyboard,
    taxi_confirm_keyboard,
    taxi_profile_keyboard,
)
from taxi.states import taxi_states
from user.i18n import t
from user.keyboards import (
    back_keyboard,
    location_keyboard,
    phone_keyboard,
    cancel_keyboard_for,
    confirm_keyboard,
    edit_keyboard,
    passenger_keyboard,
    place_keyboard,
)
from user.states import user_states


async def render_current_state(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    if "_state_before_language" in data:
        state_name = data.pop("_state_before_language")
    else:
        state_name = await state.get_state()
    await state.set_data(data)

    if not state_name:
        await message.answer(
            f"{t(lang, 'start.welcome')}\n\n{t(lang, 'role.choose')}",
            reply_markup=role_keyboard(lang),
        )
        await state.set_state(taxi_states.choosing_role)
        return

    await _send_state_prompt(message, state, state_name, lang)
    await state.set_state(state_name)


async def _send_state_prompt(message: Message, state: FSMContext, state_name: str, lang: str) -> None:
    data = await state.get_data()

    if state_name == taxi_states.choosing_role.state:
        await message.answer(t(lang, "role.choose"), reply_markup=role_keyboard(lang))
    elif state_name == taxi_states.profile.state:
        await message.answer(t(lang, "profile.menu"), reply_markup=taxi_profile_keyboard(lang))
    elif state_name == taxi_states.firstname.state:
        await message.answer(t(lang, "taxi.input.firstname"), reply_markup=ReplyKeyboardRemove())
    elif state_name == taxi_states.lastname.state:
        await message.answer(t(lang, "taxi.input.lastname"))
    elif state_name == taxi_states.contact.state:
        await message.answer(t(lang, "taxi.input.phone"), reply_markup=contact_keyboard(lang))
    elif state_name == taxi_states.car_model.state:
        await message.answer(t(lang, "taxi.input.car_model"), reply_markup=ReplyKeyboardRemove())
    elif state_name == taxi_states.car_number.state:
        await message.answer(t(lang, "taxi.input.car_number"))
    elif state_name == taxi_states.confirm.state:
        await message.answer(t(lang, "taxi.confirm"), reply_markup=taxi_confirm_keyboard(lang))
    elif state_name == taxi_states.edit_confirm.state:
        await message.answer(t(lang, "profile.edit_menu"), reply_markup=edit_profile_keyboard(lang))
    elif state_name == taxi_states.edit_firstname.state:
        await message.answer(
            f"{t(lang, 'taxi.edit.firstname')}\n\n"
            f"{t(lang, 'edit.example')}: Ali",
            reply_markup=taxi_back_keyboard(lang)
        )
    elif state_name == taxi_states.edit_lastname.state:
        await message.answer(
            f"{t(lang, 'taxi.edit.lastname')}\n\n"
            f"{t(lang, 'edit.example')}: Valiyev",
            reply_markup=taxi_back_keyboard(lang)
        )
    elif state_name == taxi_states.edit_phone.state:
        await message.answer(
            f"{t(lang, 'taxi.edit.phone')}\n\n"
            f"{t(lang, 'edit.example')}: +998901234567",
            reply_markup=taxi_back_and_phone_keyboard(lang)
        )
    elif state_name == taxi_states.edit_car_model.state:
        await message.answer(
            f"{t(lang, 'taxi.edit.car_model')}\n\n"
            f"{t(lang, 'edit.example')}: Cobalt",
            reply_markup=taxi_back_keyboard(lang)
        )
    elif state_name == taxi_states.edit_car_number.state:
        await message.answer(
            f"{t(lang, 'taxi.edit.car_number')}\n\n"
            f"{t(lang, 'edit.example')}: 01A123BC",
            reply_markup=taxi_back_keyboard(lang)
        )
    elif state_name == taxi_states.complaint_text.state:
        await message.answer(t(lang, "complaint.prompt"), reply_markup=taxi_back_keyboard(lang))
    elif state_name == user_states.choosing_language.state:
        await message.answer(t(lang, "language.choose"))
    elif state_name == user_states.choose_option.state:
        await message.answer(t(lang, "choose.option"), reply_markup=passenger_keyboard(lang))
    elif state_name == user_states.user_firstname.state:
        await message.answer(
            f"{t(lang, 'input.name')}\n{t(lang, 'edit.example')}: Ali",
            reply_markup=cancel_keyboard_for(lang)
        )
    elif state_name == user_states.user_lastname.state:
        await message.answer(
            f"{t(lang, 'input.surname')}\n{t(lang, 'edit.example')}: Valiyev",
            reply_markup=cancel_keyboard_for(lang)
        )
    elif state_name == user_states.user_phone.state:
        await message.answer(
            f"{t(lang, 'input.phone')}\n{t(lang, 'edit.example')}: +998901234567",
            reply_markup=phone_keyboard(lang)
        )
    elif state_name == user_states.user_place1.state:
        await message.answer(t(lang, "input.from"), reply_markup=place_keyboard(lang, type="from"))
    elif state_name == user_states.user_place2.state:
        await message.answer(t(lang, "input.to"), reply_markup=place_keyboard(lang, type="to"))
    elif state_name == user_states.user_confirm.state:
        await message.answer(t(lang, "input.location"), reply_markup=location_keyboard(lang))
    elif state_name == user_states.user_people.state:
        await message.answer(
            f"{t(lang, 'input.people_count')}\n{t(lang, 'edit.example')}: 2, 3, 4",
            reply_markup=cancel_keyboard_for(lang)
        )
    elif state_name == user_states.confirm_order.state:
        await _send_order_summary(message, data, lang)
    elif state_name == user_states.edit_field.state:
        await message.answer(t(lang, "edit.choose_field"), reply_markup=edit_keyboard(lang))
    elif state_name == user_states.editing_firstname.state:
        await message.answer(t(lang, "edit.firstname"), reply_markup=cancel_keyboard_for(lang))
    elif state_name == user_states.editing_lastname.state:
        await message.answer(t(lang, "edit.lastname"), reply_markup=cancel_keyboard_for(lang))
    elif state_name == user_states.editing_phone.state:
        await message.answer(t(lang, "edit.phone"), reply_markup=phone_keyboard(lang))
    elif state_name == user_states.editing_place1.state:
        await message.answer(t(lang, "edit.place1"), reply_markup=back_keyboard(lang))
        await message.answer(t(lang, "edit.place1"), reply_markup=place_keyboard(lang, "from"))
    elif state_name == user_states.editing_place2.state:
        await message.answer(t(lang, "edit.place2"), reply_markup=back_keyboard(lang))
        await message.answer(t(lang, "edit.place2"), reply_markup=place_keyboard(lang, "to"))
    elif state_name == user_states.editing_location.state:
        await message.answer(t(lang, "edit.location"), reply_markup=location_keyboard(lang))
    elif state_name == user_states.editing_people.state:
        await message.answer(t(lang, "edit.people"), reply_markup=cancel_keyboard_for(lang))
    elif state_name == user_states.complaint_text.state:
        await message.answer(t(lang, "complaint.prompt"), reply_markup=cancel_keyboard_for(lang))
    else:
        await message.answer(t(lang, "choose.option"), reply_markup=passenger_keyboard(lang))


async def _send_order_summary(message: Message, data: dict, lang: str) -> None:
    summary = (
        f"{t(lang, 'summary.title')}\n\n"
        f"{t(lang, 'summary.firstname')}: {data.get('user_firstname')}\n"
        f"{t(lang, 'summary.lastname')}: {data.get('user_lastname')}\n"
        f"{t(lang, 'summary.phone')}: {data.get('user_phone')}\n"
        f"{t(lang, 'summary.from')}: {data.get('user_place1')}\n"
        f"{t(lang, 'summary.to')}: {data.get('user_place2')}\n"
        f"{t(lang, 'summary.people')}: {data.get('user_people')}\n"
    )
    await message.answer(summary, reply_markup=confirm_keyboard(lang))
