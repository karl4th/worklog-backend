# Tech-Task (Техническое задание, High-Level)

Цель: сформулировать исходные требования для разработки backend-сервиса **WorkLog**, который по завершении должен обеспечивать функциональность, описанную далее.

> Настоящий документ является исходной точкой проекта и описывает желаемый конечный результат.
>
> Дата версии: 24-07-2025

## 0. Бизнес-ценность и назначение

* **Единое управление задачами и проектами.** Система централизует постановку, распределение и контроль выполнения задач межфункциональных команд.
* **Автоматизация бизнес-процессов.** Интеграция с AI позволяет автоматически генерировать и обновлять задачи на основании внешних сигналов (чаты, письма, отчёты).
* **Повышение прозрачности.** Подразделения, смены и роли хранятся в единой базе; руководители видят актуальный статус работы.
* **Сокращение ручных операций.** Уведомления и чек-листы минимизируют человеческий фактор.
* **Гибкая модель доступа.** RBAC даёт возможность детально настраивать права без изменения кода.
* **Масштабируемость.** Архитектура FastAPI + PostgreSQL + RabbitMQ легко масштабируется горизонтально.

## 1. Стек и окружение

| Компонент | Версия / пакет |
|-----------|----------------|
| Python    | >=3.11         |
| FastAPI   | requirements.txt (`fastapi`) |
| ASGI      | `uvicorn` |
| ORM       | `SQLAlchemy` 2 (async) + `asyncpg` |
| Миграции  | `alembic` |
| CORS      | `fastapi.middleware.cors` (разрешены origin `localhost:3000`, `ortalyk.worklog.kz`) |
| ENV       | `python-dotenv`, `pydantic-settings` |
| Docker    | Docker Engine 24+ (есть `Dockerfile`) |

После реализации установка зависимостей должна выполняться командой:
```bash
pip install -r requirements.txt
```

## 2. Структура проекта
```
backend/
├── main.py                # точка входа FastAPI
├── Dockerfile             # образ для prod/stage
├── requirements.txt       # зависимости
├── alembic.ini            # настройки миграций
├── migrations/            # автогенерация схемы БД
├── uploads/               # статика для FileResponse
└── src/worklog/           # доменные модули (см. ниже)
```

### Доменные модули (`src/worklog/*`)
Разработчик должен реализовать подпакеты, соответствующие предметным областям (модели, схемы, сервисы, view-router):

* `ai` – интеграция с AI (Claude/Anthropic) для автогенерации/обновления задач.
* `auth` – JWT-аутентификация, refresh-токены, роли.
* `blocks` – строительные блоки (справочник).
* `departments` – подразделения организации.
* `lvl4_act` – акты 4-го уровня (документооборот).
* `notifications` – центр уведомлений (RabbitMQ `pika`).
* `queue` – задачи очереди.
* `reshift` – пересменка рабочих групп.
* `rules` – RBAC: роли и права.
* `shifts` – вахтовые циклы.
* `task_checklist`, `task_comments`, `task_files` – доп. сущности задач.
* `tasks` – основной менеджер задач.
* `users` – пользователи.
* `wells` – скважины.
* `config` – настройки приложения/аутентификации.
* `db` – фабрика соединения с PostgreSQL.

## 3. Запуск приложения

1. Создать `.env` рядом с `main.py` (см. образец ниже).
2. Запустить БД PostgreSQL и задать переменные подключения.
3. Выполнить миграции:
   ```bash
   alembic upgrade head
   ```
4. Запустить сервер (dev-режим):
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   или через Docker:
   ```bash
   docker build -t worklog-backend .
   docker run -p 8000:8000 --env-file .env worklog-backend
   ```

### Пример `.env`
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=worklog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
JWT_SECRET=change_me
ANTHROPIC_API_KEY=...
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## 4. Регистрация роутов
В `main.py` вызывается `get_routes(app)`; функция импортирует все `router`-ы из доменных модулей и монтирует их.

| Модуль | Префикс | Назначение |
|--------|---------|------------|
| `auth.views.router`           | `/api/v1/auth`          | 🔑 Аутентификация |
| `users.views.router`          | `/api/v1/users`         | 👥 Пользователи |
| `tasks.views.router`          | `/api/v1/tasks`         | 🔍 Задачи |
| `task_files.views.router`     | `/api/v1/task_files`    | 🗂️ Файлы задач |
| `task_comments.views.router`  | `/api/v1/task-comments` | 💬 Комментарии |
| `task_checklist.views.router` | `/api/v1/task-checklist`| ✅ Чек-лист |
| `departments.views.router`    | `/api/v1/departments`   | 🏢 Отделы |
| `blocks.views.router`         | `/api/v1/blocks`        | 🧱 Блоки |
| `rules.views.role_router`     | `/api/v1/rules`         | 📜 Роли |
| `rules.views.permission_router`| `/api/v1/rules`        | 🔑 Права |
| `shifts.views.router`         | `/api/v1/shifts`        | ⏱️ Вахты |
| `notifications.views.router`  | `/api/v1/notifications` | 📨 Уведомления |
| `ai.views.router`             | `/api/v1/ai`            | 🤖 AI-функции |
| `reshift.views.router`        | `/api/v1/reshifts`      | 🔄 Пересменка |
| `wells.views.router`          | `/api/v1/wells`         | 💦 Скважины |

## 5. Безопасность и права доступа
RBAC реализован в `rules`:
* Таблицы `roles`, `permissions`, связывающая таблица.
* Сервис `PermissionService.user_access_control(user_id, action)` вызывается во view-функциях.
* Авторизация через Bearer-JWT (см. `auth/utils.py`).

## 6. Хранение файлов
* Загружаемые файлы сохраняются в `uploads/`.
* Для скачивания используется эндпоинт: `GET /files/{path}` (см. `main.py`).

## 7. Интеграции
* **AI (Anthropic Claude)** — генерация и обновление задач (`ai/service.py`).
* **RabbitMQ** — публикация уведомлений (`notifications/service.py`).

## 8. Как проверить
1. Создайте тестового пользователя через `/api/v1/auth/register`.
2. Получите JWT-токен через `/api/v1/auth/login`.
3. Создайте задачу: `POST /api/v1/tasks/` с заголовком `Authorization: Bearer <token>`.
4. Убедитесь, что задача видна в `/api/v1/tasks/my-tasks`.

---
Документ отражает текущую архитектуру (версия приложения 2.1.0). Для детальных схем моделей, алгоритмов и тест-примеров используйте полный вариант ТЗ (опция **B**).
