import asyncio
import unittest
from types import SimpleNamespace

from taxi.filters import (
    PhoneFilter as TaxiPhoneFilter,
    format_car_number,
    format_phone_number,
)
from user.filters import LocationFilter, PeopleCountFilter, PhoneFilter
from user.i18n import t


class FakeMessage:
    def __init__(self, text=None, contact=None, location=None, user_id=1001):
        self.text = text
        self.contact = contact
        self.location = location
        self.from_user = SimpleNamespace(id=user_id)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


def patch_language(module):
    original = module.UserService.get_user_language
    module.UserService.get_user_language = staticmethod(
        lambda telegram_id: asyncio.sleep(0, result="en")
    )
    return original


class UserFilterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import user.filters as user_filters

        self.user_filters = user_filters
        self.original_user_language = patch_language(user_filters)

    async def asyncTearDown(self):
        self.user_filters.UserService.get_user_language = self.original_user_language

    async def test_phone_filter_rejects_invalid_text(self):
        message = FakeMessage(text="abc")

        self.assertFalse(await PhoneFilter()(message, None))
        self.assertIn("Invalid phone", message.answers[-1])

    async def test_phone_filter_accepts_valid_text(self):
        message = FakeMessage(text="+998901234567")

        self.assertTrue(await PhoneFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_phone_filter_accepts_contact(self):
        message = FakeMessage(contact=SimpleNamespace(phone_number="901234567"))

        self.assertTrue(await PhoneFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_phone_filter_rejects_empty_input_with_example(self):
        message = FakeMessage()

        self.assertFalse(await PhoneFilter()(message, None))
        self.assertIn("+998901234567", message.answers[-1])

    async def test_phone_filter_ignores_cancel_button(self):
        message = FakeMessage(text="❌ Cancel")

        self.assertFalse(await PhoneFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_location_filter_rejects_non_location(self):
        message = FakeMessage(text="Toshkent")

        self.assertFalse(await LocationFilter()(message, None))
        self.assertIn("location", message.answers[-1].lower())

    async def test_location_filter_accepts_location(self):
        message = FakeMessage(location=SimpleNamespace(latitude=41.3, longitude=69.2))

        self.assertTrue(await LocationFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_location_filter_ignores_cancel_button(self):
        message = FakeMessage(text="❌ Cancel")

        self.assertFalse(await LocationFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_people_filter_rejects_text_and_out_of_range_number(self):
        text_message = FakeMessage(text="four")
        range_message = FakeMessage(text="30")

        self.assertFalse(await PeopleCountFilter()(text_message, None))
        self.assertIn("number", text_message.answers[-1].lower())

        self.assertFalse(await PeopleCountFilter()(range_message, None))
        self.assertIn("1 to 20", range_message.answers[-1])

    async def test_people_filter_rejects_zero_and_empty_text(self):
        zero_message = FakeMessage(text="0")
        empty_message = FakeMessage(text="")

        self.assertFalse(await PeopleCountFilter()(zero_message, None))
        self.assertIn("1 to 20", zero_message.answers[-1])

        self.assertFalse(await PeopleCountFilter()(empty_message, None))
        self.assertIn("number", empty_message.answers[-1].lower())

    async def test_people_filter_accepts_range(self):
        message = FakeMessage(text="4")

        self.assertTrue(await PeopleCountFilter()(message, None))
        self.assertEqual(message.answers, [])

    async def test_people_filter_ignores_cancel_button(self):
        message = FakeMessage(text="❌ Cancel")

        self.assertFalse(await PeopleCountFilter()(message, None))
        self.assertEqual(message.answers, [])


class TaxiFilterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import taxi.filters as taxi_filters

        self.taxi_filters = taxi_filters
        self.original_taxi_language = patch_language(taxi_filters)

    async def asyncTearDown(self):
        self.taxi_filters.UserService.get_user_language = self.original_taxi_language

    async def test_taxi_phone_filter_rejects_invalid_text(self):
        message = FakeMessage(text="hello")

        self.assertFalse(await TaxiPhoneFilter()(message))
        self.assertIn("Invalid phone", message.answers[-1])

    async def test_taxi_phone_filter_accepts_contact(self):
        message = FakeMessage(contact=SimpleNamespace(phone_number="901234567"))

        self.assertTrue(await TaxiPhoneFilter()(message))
        self.assertEqual(message.answers, [])

    async def test_taxi_phone_filter_rejects_empty_input_with_example(self):
        message = FakeMessage()

        self.assertFalse(await TaxiPhoneFilter()(message))
        self.assertIn("+998901234567", message.answers[-1])

    async def test_taxi_phone_filter_ignores_back_button(self):
        message = FakeMessage(text=t("en", "button.back"))

        self.assertFalse(await TaxiPhoneFilter()(message))
        self.assertEqual(message.answers, [])

    def test_taxi_format_helpers_normalize_values(self):
        self.assertEqual(format_phone_number("90 123 45 67"), "+998901234567")
        self.assertEqual(format_car_number("01 a-123 bc"), "01A123BC")


if __name__ == "__main__":
    unittest.main()
