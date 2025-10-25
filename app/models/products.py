from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.categories import Category
    from app.models.reviews import Review
    from app.models.users import User


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[Decimal] = mapped_column(Float, default=0.0)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    seller: Mapped["User"] = relationship("User", back_populates="products")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")
