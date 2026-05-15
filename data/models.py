from sqlalchemy import Float, create_engine, Column, Integer, String, BigInteger, Date, ForeignKey, UUID, BIGINT, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from sqlalchemy import DateTime
from pathlib import Path

load_dotenv()


# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")

# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = BASE_DIR / "taxi.sqlite3"
SQLITE_DATABASE_URL = os.getenv(
    "SQLITE_DATABASE_URL",
    f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH.as_posix()}",
)
POSTGRES_DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = POSTGRES_DATABASE_URL if os.getenv("USE_POSTGRES") == "1" else SQLITE_DATABASE_URL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"timeout": 10},
)

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
    telegram_id = Column(String, unique=True)
    language = Column(String(2), default="uz", nullable=False)
    last_used_at = Column(DateTime(timezone = True), default=lambda : datetime.now(timezone.utc), onupdate=lambda : datetime.now(timezone.utc))

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

    # Yangi fieldlar
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    location_message_id = Column(BIGINT, nullable=True)
    driver_id = Column(BIGINT, nullable=True)
    chat_id = Column(BIGINT, nullable=True)
    status = Column(String, default="new")

    resent = Column(Integer, default=0)

    def __repr__(self):
        return f"<Order uid={self.uid} message={self.message!r} user_id={self.user_id}>"


async def init_db() -> None:
    if not IS_SQLITE:
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("""
            DELETE FROM users
            WHERE telegram_id IS NOT NULL
              AND id NOT IN (
                  SELECT MAX(id)
                  FROM users
                  WHERE telegram_id IS NOT NULL
                  GROUP BY telegram_id
              )
        """))
        await conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_id_unique
            ON users (telegram_id)
        """))

