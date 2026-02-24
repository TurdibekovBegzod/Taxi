from sqlalchemy import Float, create_engine, Column, Integer, String, BigInteger, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Centralized DB config
DATABASE_URL = "sqlite:///taxi.db"

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    phone = Column(Integer)
    telegram_id = Column(BigInteger, unique=True)

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
    telegram_id = Column(BigInteger)
    def __repr__(self):
        return f"<Taxi id={self.id} fullname={self.fullname!r} nomer={self.nomer} car_model={self.car_model!r} car_nomer={self.car_nomer} telegram_id={self.telegram_id}>"


def create_base():
    """Convenience helper to create all tables (useful for local quick starts).
    Prefer using Alembic migrations in production."""
    Base.metadata.create_all(engine)
