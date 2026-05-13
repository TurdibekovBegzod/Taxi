import re


def phone_digits(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def normalize_phone_number(phone: str) -> str | None:
    digits = phone_digits(phone)

    if len(digits) == 9:
        return f"+998{digits}"

    if len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"

    return None


def is_valid_phone_number(phone: str) -> bool:
    return normalize_phone_number(phone) is not None
