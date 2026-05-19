# Tasks API

FastAPI-приложение для управления задачами с WebSocket-чатом по комнатам.

## Структура проекта

```
app/
├── main.py          # точка входа FastAPI
├── dependencies.py  # get_current_user, require_admin, get_storage
├── schemas.py       # Pydantic-модели
├── storage.py       # in-memory хранилище
└── routers/
    ├── tasks.py     # /tasks CRUD
    ├── users.py     # /users/me
    ├── admin.py     # /admin/stats, /admin/tasks/{id}
    └── rooms.py     # WebSocket /ws/rooms/{room_id}, /rooms/{room_id}/users
tests/
├── conftest.py
├── test_tasks.py
├── test_websocket.py
└── test_dependencies_and_routing.py
```

## Запуск локально

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Документация API: http://localhost:8000/docs

## Запуск тестов

```bash
pytest
```

## Запуск в Docker

```bash
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
curl http://localhost:8000/health
```

## API

| Метод  | Маршрут                          | Описание                        |
|--------|----------------------------------|---------------------------------|
| POST   | /tasks                           | Создать задачу                  |
| GET    | /tasks                           | Список задач пользователя       |
| GET    | /tasks/{id}                      | Получить задачу                 |
| PATCH  | /tasks/{id}/status               | Изменить статус                 |
| DELETE | /tasks/{id}                      | Удалить задачу                  |
| GET    | /users/me                        | Текущий пользователь            |
| GET    | /admin/stats                     | Статистика (только admin)       |
| DELETE | /admin/tasks/{id}                | Удалить любую задачу (admin)    |
| GET    | /health                          | Состояние приложения            |
| WS     | /ws/rooms/{room_id}?username=X   | WebSocket-чат                   |
| GET    | /rooms/{room_id}/users           | Активные пользователи комнаты   |

### Авторизация

Передавайте заголовок `X-User-Id: <integer>`.  
Для admin-маршрутов также `X-User-Role: admin`.
