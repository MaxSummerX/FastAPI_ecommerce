from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_seller
from app.depends.db_depends import get_async_db
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas.products import Product as ProductSchema
from app.schemas.products import ProductCreate


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).join(CategoryModel).where(ProductModel.is_active, CategoryModel.is_active)
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
) -> Any:
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    # Проверяем существует ли категория
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)  # Для получения id и is_active из базы
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_product_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяем, существует ли активная категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    result = await db.scalars(stmt_category)
    db_category = result.first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Получаем активные товары в категории
    stmt_product = select(ProductModel).where(ProductModel.category_id == category_id, ProductModel.is_active)
    result = await db.scalars(stmt_product)
    db_product = result.all()

    return db_product


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    # Делаем запрос на существования товара
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    result = await db.scalars(stmt_product)
    product = result.first()

    # Выводи ошибку если товара нет
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Проверяем, существует ли активная категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    result = await db.scalars(stmt_category)
    db_category = result.first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Отравляем данные
    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
) -> Any:
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    # Проверяем существует ли товар
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    result = await db.scalars(stmt_product)
    db_product = result.first()

    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")

    # Проверяем существует ли категория
    stmt_category = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    result = await db.scalars(stmt_category)
    db_category = result.first()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    # Обновление товара
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump()))
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_seller)
) -> Any:
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    result = await db.scalars(stmt)
    product = result.first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")

    product.is_active = False
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product
