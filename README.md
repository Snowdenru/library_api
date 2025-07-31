# Library Management System API

## Описание проекта

RESTful API для управления библиотечным каталогом с возможностью выполнения CRUD-операций над книгами, их поиска и получения статистики. Проект реализован на Python с использованием асинхронного фреймворка Aiohttp и базы данных SQLite.

## Функциональные возможности

- Полный CRUD для книг (создание, чтение, обновление, удаление)
- Поиск книг по различным параметрам:
  - Названию (частичное совпадение)
  - Автору (частичное совпадение)
  - Жанру (точное совпадение)
  - Году издания (диапазон)
  - ISBN (точное совпадение)
- Сортировка результатов поиска
- Пагинация для списков книг
- Получение статистики:
  - Количество книг по жанрам
  - Количество книг по авторам
- Документирование API через Swagger UI

## Технологический стек

- Python ≥ 3.10
- Aiohttp ≥ 3.8 (асинхронный веб-фреймворк)
- SQLite (база данных)
- Pydantic (валидация данных)
- Poetry (управление зависимостями)
- Docker (контейнеризация)
- Swagger UI (документация API)

## Установка и запуск

### Локальная разработка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/library_api.git
   cd library_api
   ```

2. Установите Poetry (если не установлен):
   ```bash
   pip install poetry
   ```

3. Установите зависимости:
   ```bash
   poetry install
   ```

4. Запустите приложение:
   ```bash
   poetry run python src/main.py
   ```

5. Приложение будет доступно по адресу: `http://localhost:8080`

### Запуск через Docker

1. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

2. Приложение будет доступно по адресу: `http://localhost:8080`
3. Документация Swagger UI: `http://localhost:8081`

## API Endpoints

### Книги

- `GET /api/books` - Список всех книг (с пагинацией)
- `POST /api/books` - Создание новой книги
- `GET /api/books/{id}` - Получение книги по ID
- `PUT /api/books/{id}` - Обновление книги
- `DELETE /api/books/{id}` - Удаление книги
- `GET /api/books/search` - Поиск книг

### Статистика

- `GET /api/stats/genres` - Статистика по жанрам
- `GET /api/stats/authors` - Статистика по авторам

## Примеры запросов

### Создание книги

```bash
curl -X POST "http://localhost:8080/api/books" \
-H "Content-Type: application/json" \
-d '{
  "title": "1984",
  "authors": ["Джордж Оруэлл"],
  "genres": ["Антиутопия", "Роман"],
  "publication_year": 1949,
  "isbn": "978-5-17-113626-1",
  "copies_available": 3
}'
```

### Поиск книг

```bash
curl "http://localhost:8080/api/books/search?title=1984&available_only=true"
```

## Структура проекта

```
library_api/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── book.py
│   │   └── database.py
│   ├── routes/
│   │   ├── books.py
│   │   └── stats.py
│   ├── services/
│   │   ├── book_service.py
│   │   └── search_service.py
│   └── utils/
│       ├── config.py
│       └── exceptions.py
└── tests/
    ├── unit/
    └── integration/
```

## Тестирование

Для запуска тестов выполните:

```bash
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

## Логирование

Логи приложения записываются в файл `library_api.log` и выводятся в консоль. При запуске через Docker логи можно просмотреть командой:

```bash
docker-compose logs -f library_api
```

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.