from sqlalchemy import Float, create_engine, Column, Integer, String, BigInteger, Date, ForeignKey, UUID, BIGINT
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
import os
load_dotenv()

DOCKER_DB_URL = os.getenv("DOCKER_DB_URL")
LOCAL_DB_URL = os.getenv("LOCAL_DB_URL")


DATABASE_URL = DOCKER_DB_URL

engine = create_async_engine(DATABASE_URL, echo=False)

session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    phone = Column(String(length=30))
    telegram_id = Column(BIGINT)

    def __repr__(self):
        return f"<User id={self.id} fullname={self.fullname!r} phone={self.phone} telegram_id={self.telegram_id}>"

class Taxi(Base):
    __tablename__ = "taxi"
    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    phone_number = Column(String)
    car_model = Column(String)
    car_number = Column(String)
    telegram_id = Column(BIGINT)
    def __repr__(self):
        return f"<Taxi id={self.id} fullname={self.fullname!r} nomer={self.nomer} car_model={self.car_model!r} car_nomer={self.car_nomer} telegram_id={self.telegram_id}>"

class Order(Base):
    __tablename__ = "orders"
    uid = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    message = Column(String)
    user_id = Column(BIGINT)   
    def __repr__(self):
        return f"<Order uid={self.uid} message={self.message!r} user_id={self.user_id}>"

