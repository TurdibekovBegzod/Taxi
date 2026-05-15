from data.models import User
from data.models import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone

class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id : str):
        async with AsyncSession(engine) as session:
            
            result = await session.execute(
                select(User)
                .where(User.telegram_id == telegram_id)
                .order_by(User.id.desc())
                .limit(1)
            )
            user = result.scalar_one_or_none()

            return user
        
    @staticmethod
    async def create_user(user_data : dict):
        existing_user = await UserService.get_user_by_telegram_id(
            telegram_id=str(user_data.get("telegram_id"))
        )
        if existing_user:
            return existing_user

        async with AsyncSession(engine) as session:
            user_data.setdefault("language", "uz")
            new_user = User(
                **user_data
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user
    @staticmethod
    async def update_user(telegram_id : str, user_data : dict = {}):
        async with AsyncSession(engine) as session:
            await session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    last_used_at=datetime.now(timezone.utc),
                    **user_data
                )
            )
            await session.commit()

    @staticmethod
    async def get_user_language(telegram_id: str) -> str:
        user = await UserService.get_user_by_telegram_id(telegram_id=telegram_id)
        return user.language if user and user.language else "uz"

    @staticmethod
    async def update_user_language(telegram_id: str, language: str):
        if language not in {"uz", "ru", "en"}:
            language = "uz"

        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(User)
                .where(User.telegram_id == telegram_id)
                .order_by(User.id.desc())
                .limit(1)
            )
            user = result.scalar_one_or_none()

            if user:
                user.language = language
                user.last_used_at = datetime.now(timezone.utc)
            else:
                user = User(
                    telegram_id=telegram_id,
                    language=language,
                    last_used_at=datetime.now(timezone.utc),
                )
                session.add(user)

            await session.commit()
            await session.refresh(user)
            return user
    
