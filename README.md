# MindTrace

MindTrace — AI-система диагностики мышления и ценностей.

Текущий статус проекта:
- рабочий MVP core
- Web flow проходит end-to-end
- итоговый профиль строится автоматически
- активная draft-таксономия содержит 38 вопросов
- проект упакован в Docker для запуска одной командой

## Что умеет MVP

- старт новой сессии
- возврат в незавершённую сессию
- прохождение опроса
- автоматическая обработка ответов через AI pipeline
- агрегация результатов
- построение итогового профиля
- бинарный output по `thinking_types`
- просмотр результата
- список пользовательских сессий
- expert read-only pages

## Стек

- Frontend: Next.js + TypeScript
- Backend: FastAPI
- DB: PostgreSQL
- Queue/Broker: Redis
- Worker: Celery
- AI: OpenAI Responses API

## Модели

В проекте используются только:

- `gpt-5.4-mini` — для промежуточных стадий
- `gpt-5.4` — для финальной стадии `final_profile_build`

Важно:  
`OPENAI_DEFAULT_MODEL` в `.env` — это только fallback.  
Реальное распределение моделей по стадиям задаётся через `prompt_versions` и сидится автоматически bootstrap-скриптом.

## Структура запуска

Проект запускается через Docker Compose.

Поднимаются сервисы:

- `mindtrace-postgres`
- `mindtrace-redis`
- `mindtrace-bootstrap`
- `mindtrace-backend`
- `mindtrace-worker`
- `mindtrace-frontend`

`mindtrace-bootstrap` автоматически выполняет:
- `alembic upgrade head`
- `python -m app.scripts.seed_prompt_versions`
- `python -m app.scripts.seed_taxonomy`

Это значит, что на пустой БД проект сам:
- создаёт схему
- применяет миграции
- сидит prompt versions
- сидит active taxonomy

## Требования

Нужно установить:

- Docker Desktop
- Docker Compose

## Подготовка `.env`

В корне проекта должен быть файл:

```text
.env
```
Пример содержимого:

```env
```
APP_NAME=MindTrace API
APP_ENV=dev
APP_DEBUG=true

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/mindtrace

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=

# Required for server-side frontend requests inside Docker
API_BASE_URL=http://mindtrace-backend:8000

# Public browser-side API URL
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000

# Fallback model only. Stage-specific models are defined in prompt_versions:
# answer_extract -> gpt-5.4-mini
# session_aggregate -> gpt-5.4-mini
# final_profile_build -> gpt-5.4
OPENAI_DEFAULT_MODEL=gpt-5.4-mini

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

Минимально обязательно заполнить:

OPENAI_API_KEY

## Быстрый старт
Из корня проекта:

docker compose up --build

После старта будут доступны:

Frontend: http://localhost:3000
Backend API: http://localhost:8000
Swagger: http://localhost:8000/docs

Как остановить проект

docker compose down

Как полностью сбросить БД

docker compose down -v


Это удалит volume PostgreSQL и поднимет проект заново с пустой БД.

Что считается нормальным при старте

Это ожидаемо:

- mindtrace-bootstrap выполняет миграции и сиды, затем завершает работу
- mindtrace-worker пишет warning про root user внутри контейнера
- mindtrace-frontend стартует через next start

Если mindtrace-bootstrap завершился успешно, это не ошибка.

Как проверить, что всё запустилось
- Открыть http://localhost:3000
- Нажать «Начать сессию»
- Убедиться, что открывается сессия
- Пройти опрос
- Дождаться результата
- Открыть /my-sessions
- Убедиться, что результат открывается повторно

Важные замечания
1. Draft taxonomy

Сейчас активная таксономия:

mindtrace_mvp_v2_draft_38

Это draft-набор на 38 вопросов для MVP.
Когда заказчик даст финальный question set, таксономия будет заменена новой версией.

2. Visitor flow

Сейчас пользовательская идентичность на frontend временная и хранится в браузере через localStorage.
Это нужно для MVP/demo flow без полноценной auth-системы.

3. OPENAI_BASE_URL

Обычно оставляется пустым:

OPENAI_BASE_URL=

Его нужно заполнять только если используется кастомный OpenAI-compatible endpoint, proxy или Azure-compatible base URL.

Основные пути
- / — старт сессии
- /session/[sessionId] — прохождение сессии
- /session/[sessionId]/result — результат
- /my-sessions — пользовательские сессии
- /expert/sessions — список сессий для expert panel
- /expert/session/[sessionId] — expert detail

Текущее ограничение MVP
- expert write-back пока не завершён
- voice/STT не является основным рабочим сценарием текущего MVP
- вопросник 38 — draft, не финальный утверждённый набор заказчика

Команда для полной пересборки

Если нужно пересобрать всё с нуля:

docker compose down -v
docker compose up --build
