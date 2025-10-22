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


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)) -> Any:
    """
    Возвращает список всех товаров.
    """
    stmt = (
        select(ProductModel)
        .join(CategoryModel)
        .where(ProductModel.is_active, CategoryModel.is_active, ProductModel.stock > 0)
    )
    products = db.scalars(stmt).all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> Any:
    """
    Создаёт новый товар.
    """
    # Проверяем существует ли категория
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    category = db.scalars(stmt).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_product_by_category(category_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяем, существует ли активная категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    db_category = db.scalars(stmt_category).first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Получаем активные товары в категории
    stmt_product = select(ProductModel).where(ProductModel.category_id == category_id, ProductModel.is_active)
    db_product = db.scalars(stmt_product).all()

    return db_product


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    # Делаем запрос на существования товара
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    product = db.scalars(stmt_product).first()

    # Выводи ошибку если товара нет
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Проверяем, существует ли активная категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    db_category = db.scalars(stmt_category).first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Отравляем данные
    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)) -> Any:
    """
    Обновляет товар по его ID.
    """
    # Проверяем существует ли товар
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    db_product = db.scalars(stmt_product).first()

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Проверяем существует ли категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    db_category = db.scalars(stmt_category).first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    # Обновление товара
    db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump()))
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    product = db.scalars(stmt).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # --- ORM Unit of Work Pattern ---
    # Изменяем атрибут объекта напрямую - SQLAlchemy Session автоматически
    # отслеживает это изменение в памяти (dirty object tracking).
    # На этом этапе изменение существует только в Python, БД ещё не затронута.
    product.is_active = False

    # Commit выполняет два действия:
    # 1. Flush - автоматически генерирует и выполняет SQL UPDATE:
    #    UPDATE products SET is_active = false WHERE id = ?
    # 2. Commit - фиксирует транзакцию в базе данных
    # Это паттерн "Unit of Work" - все изменения отслеженных объектов
    # сохраняются одной транзакцией без явного написания UPDATE запросов.
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
