from data.models import User
from data.models import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from datetime import datetime, timezone

class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id : str):
        async with AsyncSession(engine) as session:
            
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            return user
        
    @staticmethod
    async def create_user(user_data : dict):
        async with AsyncSession(engine) as session:
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
    
