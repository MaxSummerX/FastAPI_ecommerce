from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.products import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Создаём связь через products к category
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

    # Создаём самоссылающеюся связь для родителя parent к children
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id")

    # Создаём самоссылающеюся связь для наследника children к parent
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
