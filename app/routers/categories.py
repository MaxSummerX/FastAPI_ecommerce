from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.depends.db_depends import get_db
from app.models.categories import Category as CategoryModel
from app.schemas.categories import Category as CategorySchema
from app.schemas.categories import CategoryCreate


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: Session = Depends(get_db)) -> Any:
    """
    Возвращает список всех категорий товаров.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active)
    category = db.scalars(stmt).all()

    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)) -> Any:
    """
    Создаёт новую категорию.
    """
    # Проверяем существования parent_id, если указан
    if category.parent_id is not None:
        # Формируем запрос
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active)
        # Отправляем запрос
        parent = db.scalars(stmt).first()
        #  Проверяем результат запроса
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/category_id")
async def update_category(category_id: int) -> dict:
    """
    Обновляет категорию по её ID
    """
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}")
async def delete_category(category_id: int) -> dict:
    """
    Удаляет категорию по её ID.
    """
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}
