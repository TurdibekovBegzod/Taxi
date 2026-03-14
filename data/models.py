from sqlalchemy import Float, create_engine, Column, Integer, String, BigInteger, Date, ForeignKey, UUID
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import uuid

# Centralized DB config
DATABASE_URL = "sqlite+aiosqlite:///taxi.db"

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    phone = Column(String(length=30))
    telegram_id = Column(String)

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
    telegram_id = Column(String)
    def __repr__(self):
        return f"<Taxi id={self.id} fullname={self.fullname!r} nomer={self.nomer} car_model={self.car_model!r} car_nomer={self.car_nomer} telegram_id={self.telegram_id}>"

class Message(Base):
    __tablename__ = "message"
    uid = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    message = Column(String)

def create_base():
    """Convenience helper to create all tables (useful for local quick starts).
    Prefer using Alembic migrations in production."""
    Base.metadata.create_all(engine)
