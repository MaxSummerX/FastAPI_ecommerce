from rich.console import Console
from sqlalchemy import and_, desc, func, select

from app.database import SessionLocal
from app.models.categories import Category
from app.models.products import Product


console = Console(color_system="auto", force_terminal=True)

# Создаём контекстный менеджер для сессий
with SessionLocal() as session:
    # 1. Составление запроса
    # На этом этапе запрос ещё не выполнен — это просто объект Select
    stmt = select(Category).where(Category.is_active).order_by(Category.name)

    # 2. Выполнение запроса.
    result = session.execute(stmt).scalars().all()
    print(result)

# 1. Составление запроса

# Метод select() - основа для создания запросов в SQLAlchemy. Он определяет, какие сущности (таблицы, модели ORM) или столбцы вы хотите извлечь из базы данных. Это аналог SELECT в SQL

# Выборка всех столбцов модели Category
example_1 = select(Category)
# Выборка конкретных столбцов модели
example_2 = select(Category.id, Category.name)


# Метод where() - добавляет условия фильтрации, аналогичные WHERE в SQL

# Фильтр активных категорий
example_3 = select(Category)
# Множественные условия
example_4 = select(Category).where(and_(Category.is_active, Category.name.like("%tech%")))
# Альтернатива примеру example_4
example_5 = select(Category).where(Category.is_active).where(Category.name.like("%text%"))


# Метод order_by() - задает сортировку результатов, аналогично ORDER BY в SQL.

# Сортировка по имени по возрастанию
example_6 = select(Category).order_by(Category.name)
# Сортировка по имени по убыванию
example_7 = select(Category).order_by(desc(Category.name))
# Множественная сортировка
example_8 = select(Category).order_by(Category.is_active.desc(), desc(Category.name))


# Метод join() - позволяет объединять таблицы, аналогично JOIN в SQL. Он используется для связывания данных из нескольких таблиц через их отношения или явные условия.

# JOIN между категориями Category и Product
example_9 = select(Category, Product).join(Product, Category.id == Product.category_id)
# Явное указание связи через ORM
example_10 = select(Category).join(Category.products)


# Метод limit() - ограничивает количество возвращаемых строк, аналогично LIMIT в SQL.
# Используйте limit() для ограничения объема данных, например, при пагинации.

# Получить только 5 категорий
example_11 = select(Category).limit(5)


# Метод offset() - пропускает указанное количество строк перед возвратом результатов, аналогично OFFSET в SQL.
# Используйте вместе с limit() для реализации пагинации.

# Пропустить первые 10 категорий и взять следующие 5
example_12 = select(Category).offset(10).limit(5)

print("-" * 135)
# 2. Выполнение запроса

with SessionLocal() as session:
    # Метод execute() отправляет запрос в базу данных и возвращает объект Result, содержащий результаты.
    example_13 = select(Category).where(Category.is_active)
    console.print(f"[red]{type(example_13)}[/red]")
    result_13_1 = session.execute(example_13)
    console.print(f"[red]{type(result_13_1)}[/red]")
    # Вызывайте execute() для выполнения запроса и получения данных. Без дополнительных методов, таких как scalars(), результат будет содержать объекты Row

    print("-" * 135)

    # Метод scalars() - извлекает первый столбец из каждой строки результата, возвращая объекты ScalarResult. Обычно используется для получения ORM-объектов.
    result_13_2 = session.execute(example_13).scalars()
    # Используйте scalars() для получения списка ORM-объектов или скалярных значений (например, id или name).
    console.print(f"[red]{type(result_13_2)}[/red]")

    # Метод all() - возвращает все результаты запроса в виде списка.
    result_13_3 = session.execute(stmt).scalars().all()

    # Метод first() - возвращает первый результат запроса или None, если результат пустой
    result_13_4 = session.execute(stmt).scalars().first()
    # Используйте first() для получения единственного объекта, например, при поиске по уникальному критерию.

    # Метод scalar() - возвращает первое значение первого столбца первой строки или None, если результат пустой
    result_13_5 = session.execute(select(func.count(Category.id))).scalar()
    # Возвращает: 10 (например, количество категорий)

# Проверка данных
print("-" * 135)
with SessionLocal() as session:
    # 1. Сколько всего записей?
    total = session.scalar(select(func.count()).select_from(Category))
    print(f"\n📊 Всего категорий: {total}")

    # 2. Все категории
    all_categories = session.scalars(select(Category)).all()
    print("\n📋 Все категории:")
    for cat in all_categories:
        print(f"  - {cat.name}: is_active={cat.is_active}")

    # 3. Только активные
    active = session.scalars(select(Category).where(Category.is_active)).all()
    print(f"\n✅ Активные категории: {len(active)}")

    # 4. Только неактивные
    inactive = session.scalars(select(Category).where(Category.is_active)).all()
    print(f"\n❌ Неактивные категории: {len(inactive)}")
