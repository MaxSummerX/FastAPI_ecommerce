from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.products import Product


class OrderItem(BaseModel):
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(..., ge=0, description="Цена за единицу на момент покупки", decimal_places=2)
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции", decimal_places=2)
    product: Product | None = Field(None, description="Полная информация о товаре")

    @field_serializer("unit_price", "total_price")
    def serialize_decimals(self, value: Decimal) -> float:
        """Конвертирует Decimal в float для JSON"""
        return round(float(value), 2)


class Order(BaseModel):
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость", decimal_places=2)
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    @field_serializer("total_amount")
    def serialize_decimals(self, value: Decimal) -> float:
        """Конвертирует Decimal в float для JSON"""
        return round(float(value), 2)

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: list[Order] = Field(..., description="Заказы на текущей странице")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)
