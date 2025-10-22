from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)) -> Any:
    """
    Обновляет категорию по её ID
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    db_category = db.scalars(stmt).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active)
        parent = db.scalars(parent_stmt).first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Обновление категории
    db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(**category.model_dump()))
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    category = db.scalars(stmt).first()
    if category is None:
        print(category)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Логическое удаление категории (Установка is_active=False)
    db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Category marked as inactive"}
