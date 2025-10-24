from sqlalchemy import select
from sqlalchemy.sql import func

from app.depends.db_depends import AsyncSession
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel


async def update_product_rating(db: AsyncSession, product_id: int) -> None:
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == product_id, ReviewModel.is_active.is_(True))
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()
