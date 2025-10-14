from fastapi import FastAPI

from app.routers.categories import router


# Создаём приложение FastAPI
app = FastAPI(title="FastAPI интернет-магазин", version="0.1.0")

# Подключаем маршруты категорий
app.include_router(router)


# Корневой эндпойнт для проверки
@app.get("/")
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает
    """
    return {"message": "Добро пожаловать в API интернет-магазина"}
