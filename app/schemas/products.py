from decimal import Decimal
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """

    name: str = Field(min_length=3, max_length=100, description="Название товара (3-100 символов)")
    description: str | None = Field(None, max_length=500, description="Описание товара (до 500 символов)")
    price: Decimal = Field(gt=0, description="Цена товара (больше 0)", decimal_places=2)
    stock: int = Field(ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(description="ID категория, к которой относится товар")

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        price: Annotated[Decimal, Form(...)],
        stock: Annotated[int, Form(...)],
        category_id: Annotated[int, Form(...)],
        description: Annotated[str | None, Form()] = None,
    ) -> "ProductCreate":
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> float:
        """Конвертирует Decimal в float для JSON"""
        return round(float(value), 2)


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    rating: float = Field(description="Рейтинг товара")
    is_active: bool = Field(description="Активность товара")

    @field_serializer("price")
    def serialize_decimals(self, value: Decimal | None) -> float | None:
        """Конвертирует Decimal в float для JSON"""
        if value is None:
            return None
        return round(float(value), 2)

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """
    Список пагинации для товаров.
    """

    items: list[Product] = Field(description="Товары для текущей страницы")
    total: int = Field(ge=0, description="Общее кол-во товаров")
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Кол-во элементов на старницы")

    model_config = ConfigDict(from_attributes=True)
