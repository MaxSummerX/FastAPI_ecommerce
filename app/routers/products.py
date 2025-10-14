from fastapi import APIRouter


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_all_products() -> dict:
    """
    Возвращает список всех товаров.
    """
    return {"message": "Список всех товаров (заглушка)"}


@router.post("/")
async def create_product() -> dict:
    """
    Создаёт новый товар.
    """
    return {"message": "товар создан (заглушка)"}


@router.get("/category/{category_id}")
async def get_product_by_category(category_id: int) -> dict:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}


@router.get("/{product_id}")
async def get_product(product_id: int) -> dict:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    return {"message": f"Детали товара {product_id} (заглушка)"}


@router.put("/{product_id}")
async def update_product(product_id: int) -> dict:
    """
    Обновляет товар по его ID.
    """
    return {"message": f"Товар {product_id} обновлён (заглушка)"}


@router.delete("/{product_id}")
async def delete_product(product_id: int) -> dict:
    """
    Удаляет товар по его ID.
    """
    return {"message": f"Товар {product_id} удалён (заглушка)"}
