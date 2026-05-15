from datetime import datetime, timedelta, timezone
import uuid

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data.crud_commands import get_order, update
from data.driver_check import get_driver, is_driver
from data.models import Order
from services.users import UserService
from user.i18n import t
from user.keyboards import location_keyboard, phone_keyboard, place_keyboard, receive
from user.my_scheduler import scheduler
from user.state_render import render_current_state

from .states import user_states


async def language_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await UserService.update_user_language(
        telegram_id=str(callback.from_user.id),
        language=lang,
    )

    await callback.message.edit_text(t(lang, f"language.changed.{lang}"))
    await render_current_state(callback.message, state, lang)
    await callback.answer()


async def process_place1(call: CallbackQuery, state: FSMContext):
    lang = await UserService.get_user_language(str(call.from_user.id))
    if call.data == "place_back":
        await call.message.delete()
        await call.message.answer(t(lang, "input.phone"), reply_markup=phone_keyboard(lang))
        await state.set_state(user_states.user_phone)
        await call.answer()
        return

    place1 = call.data.split("_", 1)[1]
    data = await state.get_data()

    if data.get("user_place2") == place1:
        await call.answer(t(lang, "error.same_region"), show_alert=True)
        return

    await state.update_data(user_place1=place1)

    if data.get("editing_field") == "user_from":
        from .functions import show_order_summary

        await show_order_summary(call.message, state)
        await call.answer()
        return

    await state.set_state(user_states.user_place2)
    await call.message.answer(t(lang, "input.to"), reply_markup=place_keyboard(lang, type="to"))
    await call.answer()


async def process_place2(call: CallbackQuery, state: FSMContext):
    lang = await UserService.get_user_language(str(call.from_user.id))
    if call.data == "place_back":
        await call.message.delete()
        await call.message.answer(t(lang, "input.from"), reply_markup=place_keyboard(lang, type="from"))
        await state.set_state(user_states.user_place1)
        await call.answer()
        return

    place2 = call.data.split("_", 1)[1]
    data = await state.get_data()
    if data.get("user_place1") == place2:
        await call.answer(t(lang, "error.same_region"), show_alert=True)
        return

    await state.update_data(user_place2=place2)

    if data.get("editing_field") == "user_to":
        from .functions import show_order_summary

        await show_order_summary(call.message, state)
        await call.answer()
        return

    await state.set_state(user_states.user_confirm)
    await call.message.answer(t(lang, "input.location"), reply_markup=location_keyboard(lang))
    await call.answer()


async def _lang_for(user_id) -> str:
    return await UserService.get_user_language(str(user_id))


def _order_uuid(order_id: str):
    try:
        return uuid.UUID(str(order_id))
    except (TypeError, ValueError):
        return None


def _yes_no_keyboard(lang: str, yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "button.yes"), callback_data=yes_callback),
                InlineKeyboardButton(text=t(lang, "button.no"), callback_data=no_callback),
            ]
        ]
    )


def _driver_accept_keyboard(lang: str, passenger_id: int, order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "order.telegram_button"),
                    url=f"tg://user?id={passenger_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(lang, "order.confirm_button"),
                    callback_data=f"confirm_{order_id}",
                )
            ],
        ]
    )


def _contact_keyboard(lang: str, passenger_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "order.telegram_button"),
                    url=f"tg://user?id={passenger_id}",
                )
            ]
        ]
    )


async def accept_order(callback: CallbackQuery):
    driver_lang = await _lang_for(callback.from_user.id)

    if not await is_driver(int(callback.from_user.id)):
        await callback.answer(t(driver_lang, "order.driver_only"), show_alert=True)
        return

    driver = await get_driver(int(callback.from_user.id))
    try:
        order_id_side, user_id_side = callback.data.split("|", 1)
    except ValueError:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order_uid = _order_uuid(order_id_side.replace("accept_", ""))
    if not order_uid:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    passenger_id = order.user_id
    passenger_lang = await _lang_for(passenger_id)
    callback_user_id = user_id_side.replace("uid_", "")

    if str(passenger_id) != str(callback_user_id):
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    if str(driver.telegram_id) == str(passenger_id):
        await callback.answer(t(driver_lang, "order.self_accept"), show_alert=True)
        return

    if order.status not in (None, "new") or order.driver_id:
        await callback.answer(t(driver_lang, "order.already_accepted"), show_alert=True)
        return

    updated_order = await update(Order, {"uid": order_uid}, {
        "driver_id": driver.telegram_id,
        "chat_id": callback.message.chat.id,
        "status": "accepted",
        "resent": 0,
    })
    if not updated_order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order_id = str(order_uid)
    await callback.bot.send_message(
        chat_id=driver.telegram_id,
        text=(
            f"{t(driver_lang, 'order.accepted_driver')}\n\n"
            f"{callback.message.text}\n\n"
            f"{t(driver_lang, 'order.confirm_instruction')}"
        ),
        reply_markup=_driver_accept_keyboard(driver_lang, passenger_id, order_id),
    )

    await callback.bot.send_message(
        chat_id=passenger_id,
        text=(
            f"{t(passenger_lang, 'order.passenger_review')}\n\n"
            f"{t(passenger_lang, 'field.driver')}: {driver.firstname} {driver.lastname}\n"
            f"{t(passenger_lang, 'field.phone')}: {driver.phone_number}"
        ),
    )

    if order.location_message_id:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=order.location_message_id,
            )
        except Exception as e:
            print("Location delete error:", e)

    try:
        await callback.message.delete()
    except Exception as e:
        print("Order message delete error:", e)

    scheduler.add_job(
        send_followup_wrapper,
        trigger="date",
        run_date=datetime.now(timezone.utc) + timedelta(minutes=5),
        kwargs={"bot": callback.bot, "order_id": order_id},
        id=f"followup_{order_id}",
        replace_existing=True,
    )
    scheduler.add_job(
        send_request,
        trigger="date",
        run_date=datetime.now(timezone.utc) + timedelta(minutes=20),
        kwargs={"bot": callback.bot, "order_id": order_id},
        id=f"resend_{order_id}",
        replace_existing=True,
    )

    await callback.answer(t(driver_lang, "order.accepted_alert"))


async def contact_passenger(callback: CallbackQuery):
    driver_lang = await _lang_for(callback.from_user.id)
    if not await is_driver(str(callback.from_user.id)):
        await callback.answer(t(driver_lang, "order.driver_only"), show_alert=True)
        return

    order_uid = _order_uuid(callback.data.split("_", 1)[1])
    if not order_uid:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=t(driver_lang, "order.contact_prompt"),
        reply_markup=_contact_keyboard(driver_lang, order.user_id),
    )
    await callback.answer(t(driver_lang, "order.private_sent"), show_alert=True)


async def confirm_order(callback: CallbackQuery):
    driver_lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.split("_", 1)[1])
    if not order_uid:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return
    if str(order.driver_id) != str(callback.from_user.id):
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    passenger_lang = await _lang_for(order.user_id)
    await callback.bot.send_message(
        chat_id=order.user_id,
        text=t(passenger_lang, "order.contact_question"),
        reply_markup=_yes_no_keyboard(
            passenger_lang,
            f"client_yes_{order_uid}",
            f"client_no_{order_uid}",
        ),
    )
    await callback.answer(t(driver_lang, "order.request_sent"))


async def client_yes(callback: CallbackQuery):
    lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.split("_", 2)[2])
    if not order_uid:
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order or str(order.user_id) != str(callback.from_user.id):
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    await callback.message.edit_text(t(lang, "order.client_happy"))
    await update(Order, {"uid": order_uid}, {"status": "completed"})
    await callback.answer()


async def client_no(callback: CallbackQuery):
    lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.split("_", 2)[2])
    if not order_uid:
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order or str(order.user_id) != str(callback.from_user.id):
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    if order.driver_id:
        driver_lang = await _lang_for(order.driver_id)
        await callback.bot.send_message(
            chat_id=order.driver_id,
            text=t(driver_lang, "order.driver_contact_passenger"),
        )

    await callback.message.edit_text(t(lang, "order.passenger_not_contacted"))
    await callback.answer()


async def send_followup_questions(bot, order_id: str):
    order_uid = _order_uuid(order_id)
    if not order_uid:
        return

    order = await get_order(order_uid)
    if not order or not order.driver_id or order.status != "accepted":
        return

    driver_lang = await _lang_for(order.driver_id)
    await bot.send_message(
        chat_id=order.driver_id,
        text=t(driver_lang, "order.followup_driver_question"),
        reply_markup=_yes_no_keyboard(
            driver_lang,
            f"driver_yes_{order_uid}",
            f"driver_no_{order_uid}",
        ),
    )


async def send_followup_wrapper(bot, order_id):
    await send_followup_questions(bot, order_id)


async def send_request(bot, order_id):
    await resend_order_to_group(bot, order_id)


async def resend_order_to_group(bot, order_id: str):
    order_uid = _order_uuid(order_id)
    if not order_uid:
        return

    order = await get_order(order_uid)
    if not order or not order.message or not order.chat_id:
        return

    if order.status == "completed":
        return

    await update(Order, {"uid": order_uid}, {
        "status": "new",
        "driver_id": None,
        "resent": (order.resent or 0) + 1,
    })

    passenger_lang = await _lang_for(order.user_id)
    await bot.send_message(
        chat_id=order.chat_id,
        text=order.message,
        reply_markup=receive(str(order_uid), order.user_id, passenger_lang),
    )

    if order.lat and order.lon:
        location_msg = await bot.send_location(
            chat_id=order.chat_id,
            latitude=order.lat,
            longitude=order.lon,
        )
        await update(Order, {"uid": order_uid}, {
            "location_message_id": location_msg.message_id,
        })


async def driver_yes(callback: CallbackQuery):
    driver_lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.replace("driver_yes_", ""))
    if not order_uid:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return
    if str(order.driver_id) != str(callback.from_user.id):
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(driver_lang, "order.driver_success"))

    passenger_lang = await _lang_for(order.user_id)
    await callback.bot.send_message(
        chat_id=order.user_id,
        text=t(passenger_lang, "order.passenger_contact_question"),
        reply_markup=_yes_no_keyboard(
            passenger_lang,
            f"passenger_yes_{order_uid}",
            f"passenger_no_{order_uid}",
        ),
    )
    await callback.answer(t(driver_lang, "order.answer_accepted"))


async def driver_no(callback: CallbackQuery):
    driver_lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.replace("driver_no_", ""))
    if not order_uid:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order:
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return
    if str(order.driver_id) != str(callback.from_user.id):
        await callback.answer(t(driver_lang, "order.not_found"), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(driver_lang, "order.driver_failed"))

    passenger_lang = await _lang_for(order.user_id)
    await callback.bot.send_message(
        chat_id=order.user_id,
        text=t(passenger_lang, "order.driver_failed_passenger"),
    )

    await resend_order_to_group(callback.bot, str(order_uid))
    await callback.answer(t(driver_lang, "order.answer_accepted"))


async def passenger_yes(callback: CallbackQuery):
    lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.replace("passenger_yes_", ""))
    if not order_uid:
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order or str(order.user_id) != str(callback.from_user.id):
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "order.passenger_success"))
    await update(Order, {"uid": order_uid}, {"status": "completed"})
    await callback.answer(t(lang, "order.answer_accepted"))


async def passenger_no(callback: CallbackQuery):
    lang = await _lang_for(callback.from_user.id)
    order_uid = _order_uuid(callback.data.replace("passenger_no_", ""))
    if not order_uid:
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    order = await get_order(order_uid)
    if not order or str(order.user_id) != str(callback.from_user.id):
        await callback.answer(t(lang, "order.not_found"), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "order.passenger_failed"))

    if order.driver_id:
        driver_lang = await _lang_for(order.driver_id)
        await callback.bot.send_message(
            chat_id=order.driver_id,
            text=t(driver_lang, "order.passenger_cancelled_driver"),
        )

    await resend_order_to_group(callback.bot, str(order_uid))
    await callback.answer(t(lang, "order.answer_accepted"))
