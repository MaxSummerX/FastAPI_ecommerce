from fastapi import FastAPI

from app.database import Base, engine
from app.routers import categories, products


# Создаём таблицы
Base.metadata.create_all(engine)

# Создаём приложение FastAPI
app = FastAPI(title="FastAPI интернет-магазин", version="0.1.0")

# Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)


# Корневой эндпойнт для проверки
@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает
    """
    return {"message": "Добро пожаловать в API интернет-магазина"}
