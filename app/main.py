from fastapi import FastAPI

from app.log import log_middleware
from app.routers import categories, products, reviews, users
from app.tasks.task import call_background_task


# Создаём приложение FastAPI
app = FastAPI(title="FastAPI интернет-магазин", version="0.1.0")

app.middleware("http")(log_middleware)

# Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


# Корневой эндпойнт для проверки
@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает
    """
    return {"message": "Добро пожаловать в API интернет-магазина"}


@app.get("/test", tags=["root"])
async def hello_world(message: str) -> dict:
    call_background_task.apply_async(args=[message], expires=3600)
    return {"message": "Hello World!"}
