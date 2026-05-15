import tempfile
import unittest
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from data import crud_commands, driver_check, models
from services import users as users_service
from services.users import UserService


class DatabaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="taxi-tests-")
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path.as_posix()}",
            echo=False,
            pool_pre_ping=True,
        )

        self.original_engines = {
            models: models.engine,
            crud_commands: crud_commands.engine,
            users_service: users_service.engine,
        }
        models.engine = self.engine
        crud_commands.engine = self.engine
        users_service.engine = self.engine

        async with self.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

    async def asyncTearDown(self):
        await self.engine.dispose()
        for module, engine in self.original_engines.items():
            module.engine = engine
        self.temp_dir.cleanup()

    async def count_rows(self, model):
        async with AsyncSession(self.engine) as session:
            result = await session.execute(select(func.count()).select_from(model))
            return result.scalar_one()


class UserServiceTests(DatabaseTestCase):
    async def test_user_language_is_saved_per_telegram_user(self):
        user = await UserService.create_user({"telegram_id": "1001"})

        self.assertEqual(user.language, "uz")
        self.assertEqual(await UserService.get_user_language("1001"), "uz")

        await UserService.update_user_language("1001", "ru")
        self.assertEqual(await UserService.get_user_language("1001"), "ru")

        await UserService.update_user_language("1001", "en")
        self.assertEqual(await UserService.get_user_language("1001"), "en")

    async def test_create_user_does_not_duplicate_same_telegram_id(self):
        first = await UserService.create_user({"telegram_id": "2002"})
        second = await UserService.create_user({"telegram_id": "2002"})

        self.assertEqual(first.id, second.id)
        self.assertEqual(await self.count_rows(models.User), 1)

    async def test_invalid_language_falls_back_to_uz(self):
        await UserService.update_user_language("3003", "de")

        user = await UserService.get_user_by_telegram_id("3003")
        self.assertIsNotNone(user)
        self.assertEqual(user.language, "uz")


class TaxiDatabaseTests(DatabaseTestCase):
    async def test_taxi_profile_crud_and_driver_check(self):
        taxi = await crud_commands.add(
            models.Taxi,
            {
                "firstname": "Ali",
                "lastname": "Valiyev",
                "phone_number": "+998901234567",
                "car_model": "Cobalt",
                "car_number": "01A123BC",
                "telegram_id": 4444,
            },
        )

        self.assertEqual(taxi.firstname, "Ali")
        self.assertTrue(await driver_check.is_driver(4444))

        updated = await crud_commands.update(
            models.Taxi,
            {"telegram_id": 4444},
            {"phone_number": "+998901111111", "car_model": "Gentra"},
        )
        self.assertEqual(updated.phone_number, "+998901111111")
        self.assertEqual(updated.car_model, "Gentra")

        driver = await driver_check.get_driver(4444)
        self.assertEqual(driver.car_number, "01A123BC")

        self.assertTrue(await crud_commands.delete(models.Taxi, {"telegram_id": 4444}))
        self.assertFalse(await driver_check.is_driver(4444))


class OrderDatabaseTests(DatabaseTestCase):
    async def test_order_create_get_update_delete(self):
        order = await crud_commands.create_order("New request", user_id=5555)

        self.assertEqual(order.message, "New request")
        self.assertEqual(order.user_id, 5555)
        self.assertEqual(order.status, "new")

        fetched = await crud_commands.get_order(order.uid)
        self.assertEqual(fetched.uid, order.uid)

        updated = await crud_commands.update(
            models.Order,
            {"uid": order.uid},
            {
                "status": "accepted",
                "driver_id": 9999,
                "lat": 41.3111,
                "lon": 69.2797,
                "location_message_id": 12345,
            },
        )
        self.assertEqual(updated.status, "accepted")
        self.assertEqual(updated.driver_id, 9999)
        self.assertEqual(updated.location_message_id, 12345)

        self.assertTrue(await crud_commands.delete_order(order.uid))
        self.assertIsNone(await crud_commands.get_order(order.uid))


if __name__ == "__main__":
    unittest.main()
