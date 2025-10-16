from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления Категории.
    Используется в POST и PUT запросах.
    """

    name: str = Field(max_length=3, max_digits=50, description="Название категории (3-50 символов)")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")
    is_active: bool = Field(description="Активность категории")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")

    model_config = ConfigDict(from_attributes=True)
