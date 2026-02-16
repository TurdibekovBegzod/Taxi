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


class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    region_name = Column(String)
    def __repr__(self):
        return f"<Region id={self.id} region_name={self.region_name!r}>"


class Condition(Base):
    __tablename__ = "condition"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    def __repr__(self):
        return f"<Condition id={self.id} name={self.name!r}>"

# class Request(Base):
#     __tablename__ = "requests"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     from_region = Column(Integer, ForeignKey("regions.id"))
#     to_region = Column(Integer, ForeignKey("regions.id"))
#     date = Column(Date)
#     number_of_people = Column(Integer)
#     condition_id = Column(Integer, ForeignKey("condition.id"))
#     def __repr__(self):
#         return f"<Request id={self.id} user_id={self.user_id} from_region={self.from_region} to_region={self.to_region} date={self.date} number_of_people={self.number_of_people} condition_id={self.condition_id}>"

# class Complaint(Base):
#     __tablename__ = "complaints"
#     id = Column(Integer, primary_key=True)
#     info = Column(String)
#     def __repr__(self):
#         return f"<Complaint id={self.id} info={self.info!r}>"

class Taxi(Base):
    __tablename__ = "user_taxi"
    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    nomer = Column(Integer)
    car_model = Column(String)
    car_nomer = Column(Integer)
    telegram_id = Column(BigInteger)
    def __repr__(self):
        return f"<Taxi id={self.id} fullname={self.fullname!r} nomer={self.nomer} car_model={self.car_model!r} car_nomer={self.car_nomer} telegram_id={self.telegram_id}>"

class User_taxi(Base):
    __tablename__ = "users_taxi"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    nomer = Column(Integer)
    car_model = Column(String)
    car_nomer = Column(Integer)
    telegram_id = Column(BigInteger)
    def __repr__(self):
        return f"<User_taxi id={self.id} full_name={self.full_name!r} nomer={self.nomer} car_model={self.car_model!r} car_nomer={self.car_nomer} telegram_id={self.telegram_id}>"

def create_base():
    """Convenience helper to create all tables (useful for local quick starts).
    Prefer using Alembic migrations in production."""
    Base.metadata.create_all(engine)
