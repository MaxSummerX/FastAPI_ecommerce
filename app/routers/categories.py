from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.depends.db_depends import get_async_db
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.schemas.categories import Category as CategorySchema
from app.schemas.categories import CategoryCreate


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)) -> Any:
    """
    Возвращает список всех категорий товаров.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active)
    result = await db.scalars(stmt)
    category = result.all()
    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Создаёт новую категорию.
    """
    # Проверяем существования parent_id, если указан
    if category.parent_id is not None:
        # Формируем запрос
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active)
        # Отправляем запрос
        result = await db.scalars(stmt)
        parent = result.first()
        #  Проверяем результат запроса
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can perform this action")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Обновляет категорию по её ID
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active)
        result = await db.scalars(parent_stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can perform this action")

    # Обновление категории
    update_date = category.model_dump(exclude_unset=True)  # exclude_unset - обновляем только переданные поля
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(**update_date))
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_user)
) -> Any:
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can perform this action")

    # Логическое удаление категории (Установка is_active=False)
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    await db.commit()

    return db_category
