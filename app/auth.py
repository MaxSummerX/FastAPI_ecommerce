from datetime import UTC, datetime, timedelta
from typing import cast

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALGORITHM, SECRET_KEY
from app.depends.db_depends import get_async_db
from app.models.users import User as UserModel


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    # Генерируем соль в байтах
    salt = bcrypt.gensalt(rounds=12)
    # Получаем хэш пароля в байтах с использованием соли
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Возвращаем сам хэш пароля
    return cast(str, hashed.decode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    # Преобразуем в байты
    hashed_bytes = hashed_password.encode("utf-8")
    # Возвращаем результат проверки пароля
    return cast(bool, bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes))


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT с payload (sub, role, id, exp).
    """
    # Создаём копию входного словаря
    to_encode = data.copy()
    # Вычисляет время истечения токена
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Добавляет поле exp (expiration) в payload токена
    to_encode.update({"exp": expire})
    # Возвращаем строку токена
    return cast(str, jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> UserModel:
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}
        ) from None

    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    result = await db.scalars(select(UserModel).where(UserModel.email == email, UserModel.is_active))
    user = cast(UserModel | None, result.first())

    if user is None:
        raise credentials_exception

    return user


async def get_current_seller(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Проверяет, что пользователь имеет роль 'seller'.
    """
    if current_user.role != "seller":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sellers can perform this action")

    return current_user
