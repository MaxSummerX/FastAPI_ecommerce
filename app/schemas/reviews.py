from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    """
    Модель для создания и обновления Отзыва.
    Используется в POST и PUT запросах.
    """

    product_id: int = Field(description="Уникальный идентификатор товара")
    comment: str | None = Field(None, description="Отзыв о товаре")
    grade: int = Field(ge=1, le=5, description="Оценка товара")


class Review(BaseModel):
    """
    Модель для ответа с данными Отзыва.
    Используется в GET запросах.
    """

    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="Уникальный идентификатор пользователя")
    product_id: int = Field(description="Уникальный идентификатор товара")
    comment: str | None = Field(None, description="Отзыв о товаре")
    comment_date: datetime = Field(description="Дата и время создания отзыва")
    grade: int = Field(description="Оценка товара")
    is_active: bool = Field(description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)
