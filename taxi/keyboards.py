from aiogram.types import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton


LABELS = {
    "role.driver": {"uz": "🚖 Haydovchi", "ru": "🚖 Водитель", "en": "🚖 Driver"},
    "role.passenger": {"uz": "👤 Yo'lovchi", "ru": "👤 Пассажир", "en": "👤 Passenger"},
    "button.sign_up": {"uz": "Ro'yxatdan o'tish", "ru": "Зарегистрироваться", "en": "Sign up"},
    "button.send_phone": {"uz": "📱 Telefon raqamini yuborish", "ru": "📱 Отправить номер телефона", "en": "📱 Send phone number"},
    "button.confirm": {"uz": "Tasdiqlash", "ru": "Подтвердить", "en": "Confirm"},
    "taxi.button.info": {"uz": "📄 Ma'lumot", "ru": "📄 Информация", "en": "📄 Info"},
    "taxi.button.edit_info": {"uz": "📝 Ma'lumotlarni o'zgartirish", "ru": "📝 Изменить данные", "en": "📝 Edit info"},
    "passenger.channel": {"uz": "📢 Kanalga o'tish", "ru": "📢 Перейти в канал", "en": "📢 Open channel"},
    "passenger.complaints": {"uz": "Shikoyatlar va takliflar", "ru": "Жалобы и предложения", "en": "Complaints and suggestions"},
    "field.firstname": {"uz": "Ism", "ru": "Имя", "en": "First name"},
    "field.lastname": {"uz": "Familiya", "ru": "Фамилия", "en": "Last name"},
    "field.phone": {"uz": "Telefon", "ru": "Телефон", "en": "Phone"},
    "field.car_model": {"uz": "Mashina modeli", "ru": "Модель машины", "en": "Car model"},
    "field.car_number": {"uz": "Mashina raqami", "ru": "Номер машины", "en": "Car number"},
    "button.back": {"uz": "◀️ Orqaga", "ru": "◀️ Назад", "en": "◀️ Back"},
}


def t(lang: str, key: str) -> str:
    values = LABELS.get(key, {})
    return values.get(lang) or values.get("uz") or key


def role_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "role.driver")),
                KeyboardButton(text=t(lang, "role.passenger")),
            ]
        ],
        resize_keyboard=True
    )


def sign_up_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "button.sign_up"))]
        ],
        resize_keyboard=True
    )


def contact_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "button.send_phone"), request_contact=True)]
        ],
        resize_keyboard=True
    )


def taxi_confirm_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "button.confirm"))]
        ],
        resize_keyboard=True
    )


def taxi_profile_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "taxi.button.info")),
                KeyboardButton(text=t(lang, "taxi.button.edit_info")),
            ],
            [KeyboardButton(text=t(lang, "passenger.channel"))],
            [KeyboardButton(text=t(lang, "passenger.complaints"))],
        ],
        resize_keyboard=True
    )


def edit_profile_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "field.firstname")), KeyboardButton(text=t(lang, "field.lastname"))],
            [KeyboardButton(text=t(lang, "field.phone")), KeyboardButton(text=t(lang, "field.car_model"))],
            [KeyboardButton(text=t(lang, "field.car_number"))],
            [KeyboardButton(text=t(lang, "button.back"))],
        ],
        resize_keyboard=True
    )


def taxi_back_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "button.back"))]
        ],
        resize_keyboard=True
    )


def taxi_back_and_phone_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "button.back")),
                KeyboardButton(text=t(lang, "button.send_phone"), request_contact=True),
            ]
        ],
        resize_keyboard=True
    )


show_role_buttons = role_keyboard("uz")
sign_up = sign_up_keyboard("uz")
get_contact = contact_keyboard("uz")
confirm = taxi_confirm_keyboard("uz")
taxi_profile = taxi_profile_keyboard("uz")
edit_profile = edit_profile_keyboard("uz")
btn_back = taxi_back_keyboard("uz")
btn_back_and_phone = taxi_back_and_phone_keyboard("uz")
