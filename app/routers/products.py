from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.depends.db_depends import get_db
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas.products import Product as ProductSchema
from app.schemas.products import ProductCreate


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)) -> Any:
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active)
    products = db.scalars(stmt).all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> Any:
    """
    Создаёт новый товар.
    """
    # Проверяем существует ли категория
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}")
async def get_product_by_category(category_id: int) -> dict:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    # Дела запрос на существования товара
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    product = db.scalars(stmt_product).first()

    # Выводи ошибку если товара нет
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Выводи ошибку если категории нет
    if product.category is None or not product.category.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    # Отравляем данные
    return product


@router.put("/{product_id}")
async def update_product(product_id: int) -> dict:
    """
    Обновляет товар по его ID.
    """
    return {"message": f"Товар {product_id} обновлён (заглушка)"}


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    product = db.scalars(stmt).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
