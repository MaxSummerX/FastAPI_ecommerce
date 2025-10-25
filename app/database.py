import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


load_dotenv()

# Строка подключения для PostgreSQl
DATABASE_URL = os.environ["POSTGRESQL"]

# Создаём engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


# Определяем базовый класс для моделей
class Base(DeclarativeBase):
    pass
