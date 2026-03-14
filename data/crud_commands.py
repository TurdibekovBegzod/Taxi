from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from data.models import engine # sizning async_engine import qilinishi kerak

async def add(model, data: dict):
    async with AsyncSession(engine) as session:
        obj = model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

async def update(model, filters: dict, updates: dict):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(model).filter_by(**filters))
        obj = result.scalar_one_or_none()
        if obj:
            for k, v in updates.items():
                setattr(obj, k, v)
            await session.commit()
            await session.refresh(obj)
            return obj

async def delete(model, filters: dict):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(model).filter_by(**filters))
        obj = result.scalar_one_or_none()
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False

async def get(model, filters: dict):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(model).filter_by(**filters))
        obj = result.scalar_one_or_none()
        return obj