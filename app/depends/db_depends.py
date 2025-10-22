from collections.abc import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.database import SessionLocal, async_session_maker


def get_db() -> Generator[Session]:
    """
    Зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и закрывает её после обработки.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------- Асинхронная сессия -------------------------


async def get_async_db() -> AsyncGenerator[AsyncSession]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
