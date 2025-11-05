FROM python:3.12-alpine

# устанавливаем переменные окружения
ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# создаем домашнюю директорию для пользователя(/home/fast) и директорию для проекта(/home/fast/app)
# создаем группу fast
# создаем отдельного пользователя fast
RUN mkdir -p $APP_HOME \
  && addgroup -S fast \
  && adduser -S fast -G fast

# устанавливаем рабочую директорию
WORKDIR $HOME

# копирование конфигурации проекта (для setuptools)
COPY pyproject.toml .

# копирование проекта FastAPI в рабочую директорию
COPY app app
COPY alembic.ini .env .

# обновление pip
# установка зависимостей из pyproject.toml
# изменение владельца, для всех директорий и файлов проекта, на пользователя fast
RUN pip install --upgrade pip setuptools wheel \
 && pip install -e . \
 && chown -R fast:fast .

# изменение рабочего пользователя на fast
USER fast
