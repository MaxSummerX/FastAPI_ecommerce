from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_async_db, get_current_buyer, get_current_user
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas.reviews import Review as ReviewSchema
from app.schemas.reviews import ReviewCreate
from app.utils.utils import check_grade, update_product_rating


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)) -> list[ReviewModel]:
    """
    Возвращает список всех отзывов.
    """
    result_review = await db.scalars(select(ReviewModel).where(ReviewModel.is_active.is_(True)))
    return cast(list[ReviewModel], result_review.all())


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_buyer)
) -> ReviewModel:
    """
    Создаёт новый отзыв, привязанный к текущему покупателю (только для 'buyer').
    """
    result_product = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active.is_(True))
    )
    db_product = result_product.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    if not check_grade(review.grade):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Grade outside the range 1–5")

    result_user = await db.scalars(
        select(ReviewModel).where(ReviewModel.product_id == review.product_id, ReviewModel.user_id == current_user.id)
    )
    db_user = result_user.first()

    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user has already left a review")

    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, review.product_id)
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_user)
) -> dict:
    """
    Выполняет мягкое удаление отзыва (только для 'admin').
    """
    result_review = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active.is_(True))
    )
    db_review = result_review.first()

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can perform this action")

    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")

    db_review.is_active = False

    await db.commit()
    await update_product_rating(db, db_review.product_id)

    return {"message": "Review deleted"}
