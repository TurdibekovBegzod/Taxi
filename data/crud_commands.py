from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from data.models import engine # sizning async_engine import qilinishi kerak
from data.models import Order


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
    
async def create_order(message : str, user_id: int) -> Order:
     async with AsyncSession(engine) as session:
        new_order = Order()
        new_order.message = message
        new_order.user_id = user_id

        session.add(new_order)

        await session.commit()
        await session.refresh(new_order)
        return new_order
     


async def delete_order(message_uid):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Order).where(Order.uid == message_uid)
        )
        order = result.scalar_one_or_none()

        if order:
            await session.delete(order)
            await session.commit()
            return True
        
        return False
    
async def get_order(order_id) -> Order:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Order).where(Order.uid == order_id)
        )
        order = result.scalar_one_or_none()
        return order


