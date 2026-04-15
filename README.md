# MindTrace

MindTrace — AI-система диагностики мышления и ценностей.

## Текущий статус проекта

- рабочий MVP core
- web flow проходит end-to-end
- итоговый профиль строится автоматически
- активная draft-таксономия содержит 38 вопросов
- проект упакован в Docker для запуска одной командой
- Telegram bot работает как точка входа в Mini App

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
- Telegram bot как точка входа
- запуск Mini App внутри Telegram
- прохождение опроса через web / Mini App интерфейс

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
- `mindtrace-telegram-bot`

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
APP_NAME=MindTrace API
APP_ENV=dev
APP_DEBUG=true

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/mindtrace

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=

# Telegram bot / Mini App
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBAPP_URL=

# Fallback model only. Stage-specific models are defined in prompt_versions:
# answer_extract -> gpt-5.4-mini
# session_aggregate -> gpt-5.4-mini
# final_profile_build -> gpt-5.4
OPENAI_DEFAULT_MODEL=gpt-5.4-mini

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

Минимально обязательно заполнить:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN` — если хотите запускать Telegram bot сервис

Примечания:

- `TELEGRAM_WEBAPP_URL` нужен для Telegram Mini App
- для локального тестирования Mini App можно использовать публичный HTTPS URL через ngrok
- если Mini App не нужен, Telegram bot можно не использовать

## Быстрый старт

Из корня проекта:

```bash
docker compose up --build
```

После старта будут доступны:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Как остановить проект

```bash
docker compose down
```

## Как полностью сбросить БД

```bash
docker compose down -v
```

Это удалит volume PostgreSQL и поднимет проект заново с пустой БД.

## Что считается нормальным при старте

Это ожидаемо:

- `mindtrace-bootstrap` выполняет миграции и сиды, затем завершает работу
- `mindtrace-worker` пишет warning про root user внутри контейнера
- `mindtrace-frontend` стартует через `next start`

Если `mindtrace-bootstrap` завершился успешно, это не ошибка.

## Как проверить, что всё запустилось

### Web flow

1. Открыть `http://localhost:3000`
2. Нажать **«Начать сессию»**
3. Убедиться, что открывается сессия
4. Пройти опрос
5. Дождаться результата
6. Открыть `/my-sessions`
7. Убедиться, что результат открывается повторно

### Telegram Mini App

После запуска проекта:

1. Убедитесь, что frontend доступен по публичному HTTPS URL
2. Укажите этот URL в `TELEGRAM_WEBAPP_URL`
3. Укажите `TELEGRAM_BOT_TOKEN` вашего бота
4. Поднимите сервис:

```bash
docker compose up -d --build mindtrace-telegram-bot
```

5. В Telegram откройте вашего бота и отправьте `/start`
6. Нажмите кнопку **«Открыть диагностику»**

## Telegram Bot / Mini App

Проект поддерживает Telegram bot как точку входа в диагностику.

Текущий сценарий:

- пользователь открывает Telegram-бота
- нажимает кнопку открытия Mini App
- Mini App открывает frontend внутри Telegram
- пользователь может начать или продолжить диагностическую сессию

Для работы Telegram Mini App нужен публичный HTTPS URL frontend.  
Для локального тестирования можно использовать ngrok.

Пример:

- frontend: `https://your-frontend-domain.ngrok-free.dev`
- этот URL указывается в `TELEGRAM_WEBAPP_URL`
- тот же домен нужно привязать к боту через BotFather

## Важно: тестирование на своих ключах

В проекте нет общих OpenAI ключей и общего универсального Telegram-бота для независимого тестирования.

Если вы хотите запускать MindTrace на своих ключах, нужно:

1. Клонировать проект из GitHub
2. Заполнить свой `.env`
3. Указать свой `OPENAI_API_KEY`
4. Создать своего Telegram-бота через BotFather
5. Указать свой `TELEGRAM_BOT_TOKEN`
6. Поднять frontend/backend через Docker Compose
7. Пробросить frontend через публичный HTTPS URL, например через ngrok
8. Указать этот URL в `TELEGRAM_WEBAPP_URL`
9. Привязать домен Mini App в BotFather
10. После этого тестировать уже через своего Telegram-бота

Иными словами:

- для demo можно использовать уже поднятый чей-то стенд
- для тестирования на своих ключах каждый участник должен поднимать проект у себя и использовать своего бота

## Важные замечания

### Draft taxonomy

Сейчас активная таксономия:

```text
mindtrace_mvp_v2_draft_38
```

Это draft-набор на 38 вопросов для MVP.

Текущий набор вопросов лежит в:

```text
backend/app/scripts/seed_taxonomy.py
```

Когда заказчик даст финальный question set, нужно создавать новую версию taxonomy, а не молча переписывать текущую active taxonomy.

### Visitor flow

Сейчас пользовательская идентичность на frontend временная и хранится в браузере через `localStorage`. Это нужно для MVP/demo flow без полноценной auth-системы.

### Prompt layer

Versioned prompt layer лежит в:

```text
backend/app/scripts/seed_prompt_versions.py
```

Текущий pipeline разделён по этапам:

- `answer_extract`
- `session_aggregate`
- `final_profile_build`

### OPENAI_BASE_URL

Обычно оставляется пустым:

```env
OPENAI_BASE_URL=
```

Его нужно заполнять только если используется кастомный OpenAI-compatible endpoint, proxy или Azure-compatible base URL.

## Основные пути

- `/` — старт сессии
- `/session/[sessionId]` — прохождение сессии
- `/session/[sessionId]/result` — результат
- `/my-sessions` — пользовательские сессии
- `/expert/sessions` — список сессий для expert panel
- `/expert/session/[sessionId]` — expert detail

## Текущее ограничение MVP

- `expert write-back` пока не завершён
- `voice/STT` не является основным рабочим сценарием текущего MVP
- текущий вопросник на 38 вопросов — draft, не финальный утверждённый набор заказчика

## Команда для полной пересборки

Если нужно пересобрать всё с нуля:

```bash
docker compose down -v
docker compose up --build
```

## MVP acceptance criteria

Текущая версия MVP должна соответствовать следующим базовым критериям приёмки:

- Question set MVP: до 38 вопросов в активной taxonomy draft-версии
- Система должна сохранять ответы, промежуточные AI-результаты, агрегат сессии и final profile
- По каждому типу мышления final profile должен возвращать бинарный output: `present` / `absent`
- Итоговый профиль должен содержать как минимум `thinking_types`, `user_view` и `expert_view`
- Telegram + Web остаются целевыми каналами MVP, при этом основной диагностический flow проходит через web / Mini App интерфейс
- Экспертная панель входит в MVP как базовый слой проверки результатов

Целевые KPI для MVP:

- Agreement with expert: не ниже 80%
- Reproducibility: не ниже 90% при одинаковом input bundle, prompt version, taxonomy version и model
- AI analysis latency for single answer: p95 не более 5 секунд
- Completed sessions rate: не ниже 95% для корректно начатых пользовательских сессий

## Что относится к phase 2, а не к текущему MVP

- адаптивный опрос
- fine-tuning собственной модели
- сложная BI-аналитика
- enterprise-роли и расширенный RBAC
- recommendation engine
- advanced A/B testing
