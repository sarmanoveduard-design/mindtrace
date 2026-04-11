# MindTrace — DB Schema v1

## 1. Общие правила

- DB: PostgreSQL (Supabase)
- Основная схема: `mindtrace`
- Все PK: `uuid`
- Все даты: `timestamptz`
- Для структурированных AI-данных: `jsonb`
- Клиенты не работают с доменными таблицами напрямую
- Все миграции только через Alembic
- Source of truth: PostgreSQL

---

## 2. Справочник статусов

### user_role
- `user`
- `expert`
- `admin`

### session_status
- `created`
- `in_progress`
- `processing`
- `completed`
- `ready`
- `failed`
- `archived`

### question_type
- `text`
- `single_choice`
- `multi_choice`
- `scale`

### taxonomy_status
- `draft`
- `active`
- `archived`

### prompt_status
- `draft`
- `active`
- `archived`

### ai_stage_code
- `answer_precheck`
- `answer_extract`
- `session_aggregate`
- `final_profile_build`
- `final_profile_summary`

### processing_status
- `queued`
- `processing`
- `done`
- `failed`

### final_profile_status
- `queued`
- `processing`
- `ready`
- `failed`
- `reviewed`

### review_status
- `pending`
- `reviewed`
- `approved`
- `rejected`

### answer_source
- `web`
- `telegram`
- `mini_app`

### session_channel
- `web`
- `telegram`
- `mini_app`

### ai_job_status
- `queued`
- `started`
- `retry`
- `succeeded`
- `failed`
- `dead`

### ai_job_type
- `answer_extract`
- `session_aggregate`
- `final_profile`

### ai_job_entity_type
- `answer`
- `session`
- `profile`

---

## 3. Таблицы

## 3.1. users

Назначение: единый профиль пользователя.

### columns
- `id uuid pk`
- `supabase_auth_id uuid null unique`
- `telegram_user_id bigint null unique`
- `telegram_username text null`
- `display_name text not null`
- `role text not null default 'user'`
- `locale text not null default 'ru'`
- `timezone text not null default 'UTC'`
- `is_active boolean not null default true`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### constraints
- role in (`user`, `expert`, `admin`)

### indexes
- unique index on `supabase_auth_id`
- unique index on `telegram_user_id`
- index on `role`

---

## 3.2. taxonomy_versions

Назначение: версия диагностической структуры.

### columns
- `id uuid pk`
- `code text not null unique`
- `version_label text not null`
- `status text not null`
- `title text not null`
- `description text null`
- `schema_json jsonb not null default '{}'::jsonb`
- `rules_json jsonb not null default '{}'::jsonb`
- `created_by uuid null references mindtrace.users(id) on delete set null`
- `created_at timestamptz not null default now()`
- `published_at timestamptz null`

### constraints
- status in (`draft`, `active`, `archived`)

### indexes
- unique index on `code`
- index on `status`

---

## 3.3. questions

Назначение: вопросы внутри версии taxonomy.

### columns
- `id uuid pk`
- `taxonomy_version_id uuid not null references mindtrace.taxonomy_versions(id) on delete cascade`
- `code text not null`
- `order_no integer not null`
- `title text not null`
- `description text null`
- `question_type text not null`
- `is_required boolean not null default true`
- `is_active boolean not null default true`
- `ui_config jsonb not null default '{}'::jsonb`
- `validation_rules jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### constraints
- question_type in (`text`, `single_choice`, `multi_choice`, `scale`)
- unique (`taxonomy_version_id`, `code`)
- unique (`taxonomy_version_id`, `order_no`)
- check `order_no > 0`

### indexes
- index on (`taxonomy_version_id`, `order_no`)
- index on (`taxonomy_version_id`, `is_active`)

---

## 3.4. sessions

Назначение: диагностическая сессия пользователя.

### columns
- `id uuid pk`
- `user_id uuid not null references mindtrace.users(id) on delete cascade`
- `taxonomy_version_id uuid not null references mindtrace.taxonomy_versions(id) on delete restrict`
- `channel text not null`
- `status text not null default 'created'`
- `current_question_order integer not null default 1`
- `started_at timestamptz not null default now()`
- `completed_at timestamptz null`
- `last_activity_at timestamptz not null default now()`
- `meta_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### constraints
- channel in (`web`, `telegram`, `mini_app`)
- status in (`created`, `in_progress`, `processing`, `completed`, `ready`, `failed`, `archived`)
- check `current_question_order > 0`

### indexes
- index on (`user_id`, `status`)
- index on (`taxonomy_version_id`, `status`)
- index on `last_activity_at`

### special index
Нужен partial unique index:
- один пользователь не может иметь больше одной активной сессии на одну taxonomy version
- активные статусы:
  - `created`
  - `in_progress`
  - `processing`

Индекс:
- unique (`user_id`, `taxonomy_version_id`)
- where status in (`created`, `in_progress`, `processing`)

---

## 3.5. answers

Назначение: ответы пользователя с ревизиями.

### columns
- `id uuid pk`
- `session_id uuid not null references mindtrace.sessions(id) on delete cascade`
- `question_id uuid not null references mindtrace.questions(id) on delete restrict`
- `revision_no integer not null`
- `answer_text text null`
- `answer_payload jsonb null`
- `source text not null`
- `is_current boolean not null default true`
- `ai_status text not null default 'pending'`
- `client_event_id text null`
- `submitted_at timestamptz not null default now()`
- `created_at timestamptz not null default now()`

### constraints
- source in (`web`, `telegram`, `mini_app`)
- ai_status in (`pending`, `queued`, `processing`, `done`, `failed`)
- unique (`session_id`, `question_id`, `revision_no`)
- check `revision_no > 0`
- check `answer_text is not null or answer_payload is not null`

### indexes
- index on (`session_id`, `question_id`)
- index on (`session_id`, `is_current`)
- index on `ai_status`
- unique index on `client_event_id` where `client_event_id is not null`

### special index
Нужен partial unique index:
- только один current-answer на пару (`session_id`, `question_id`)
- unique (`session_id`, `question_id`)
- where `is_current = true`

---

## 3.6. prompt_versions

Назначение: версии промптов по этапам AI pipeline.

### columns
- `id uuid pk`
- `stage_code text not null`
- `version_label text not null`
- `status text not null`
- `system_prompt text not null`
- `developer_prompt text null`
- `schema_json jsonb not null default '{}'::jsonb`
- `model_config_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `created_by uuid null references mindtrace.users(id) on delete set null`

### constraints
- stage_code in (
  `answer_precheck`,
  `answer_extract`,
  `session_aggregate`,
  `final_profile_build`,
  `final_profile_summary`
)
- status in (`draft`, `active`, `archived`)
- unique (`stage_code`, `version_label`)

### indexes
- index on (`stage_code`, `status`)

---

## 3.7. answer_extractions

Назначение: AI-результаты по каждому ответу.

### columns
- `id uuid pk`
- `answer_id uuid not null references mindtrace.answers(id) on delete cascade`
- `session_id uuid not null references mindtrace.sessions(id) on delete cascade`
- `question_id uuid not null references mindtrace.questions(id) on delete restrict`
- `stage_code text not null`
- `prompt_version_id uuid not null references mindtrace.prompt_versions(id) on delete restrict`
- `status text not null`
- `model_name text not null`
- `input_snapshot jsonb not null default '{}'::jsonb`
- `raw_output_text text null`
- `normalized_output jsonb not null default '{}'::jsonb`
- `confidence_score numeric(5,4) null`
- `token_usage_json jsonb not null default '{}'::jsonb`
- `error_text text null`
- `started_at timestamptz null`
- `finished_at timestamptz null`
- `created_at timestamptz not null default now()`

### constraints
- stage_code in (`answer_precheck`, `answer_extract`)
- status in (`queued`, `processing`, `done`, `failed`)
- check `confidence_score is null or (confidence_score >= 0 and confidence_score <= 1)`

### indexes
- index on (`answer_id`, `stage_code`)
- index on `session_id`
- index on `status`
- gin index on `normalized_output`

---

## 3.8. session_aggregates

Назначение: накопленный агрегат сессии.

### columns
- `id uuid pk`
- `session_id uuid not null references mindtrace.sessions(id) on delete cascade`
- `stage_code text not null default 'session_aggregate'`
- `prompt_version_id uuid not null references mindtrace.prompt_versions(id) on delete restrict`
- `status text not null`
- `aggregate_json jsonb not null default '{}'::jsonb`
- `coverage_json jsonb not null default '{}'::jsonb`
- `confidence_json jsonb not null default '{}'::jsonb`
- `raw_output_text text null`
- `error_text text null`
- `updated_at timestamptz not null default now()`
- `created_at timestamptz not null default now()`

### constraints
- stage_code in (`session_aggregate`)
- status in (`queued`, `processing`, `done`, `failed`)

### indexes
- index on (`session_id`, `created_at desc`)
- index on `status`
- gin index on `aggregate_json`

---

## 3.9. final_profiles

Назначение: финальный профиль по завершённой сессии.

### columns
- `id uuid pk`
- `session_id uuid not null references mindtrace.sessions(id) on delete cascade`
- `prompt_version_id uuid not null references mindtrace.prompt_versions(id) on delete restrict`
- `status text not null`
- `profile_json jsonb not null default '{}'::jsonb`
- `summary_text text null`
- `confidence_json jsonb not null default '{}'::jsonb`
- `raw_output_text text null`
- `published_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### constraints
- status in (`queued`, `processing`, `ready`, `failed`, `reviewed`)
- unique (`session_id`)

### indexes
- unique index on `session_id`
- index on `status`
- gin index on `profile_json`

---

## 3.10. expert_reviews

Назначение: экспертная оценка качества результата.

### columns
- `id uuid pk`
- `session_id uuid not null references mindtrace.sessions(id) on delete cascade`
- `final_profile_id uuid not null references mindtrace.final_profiles(id) on delete cascade`
- `reviewer_user_id uuid not null references mindtrace.users(id) on delete restrict`
- `status text not null default 'pending'`
- `quality_score integer null`
- `notes_text text null`
- `corrections_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

### constraints
- status in (`pending`, `reviewed`, `approved`, `rejected`)
- check `quality_score is null or (quality_score between 1 and 5)`

### indexes
- index on `session_id`
- index on (`reviewer_user_id`, `status`)
- index on `quality_score`

---

## 3.11. ai_jobs

Назначение: жизненный цикл AI-задач.

### columns
- `id uuid pk`
- `job_type text not null`
- `entity_type text not null`
- `entity_id uuid not null`
- `session_id uuid null references mindtrace.sessions(id) on delete cascade`
- `status text not null`
- `priority integer not null default 100`
- `attempt_no integer not null default 0`
- `max_attempts integer not null default 3`
- `idempotency_key text not null`
- `payload_json jsonb not null default '{}'::jsonb`
- `error_text text null`
- `scheduled_at timestamptz not null default now()`
- `started_at timestamptz null`
- `finished_at timestamptz null`
- `created_at timestamptz not null default now()`

### constraints
- job_type in (`answer_extract`, `session_aggregate`, `final_profile`)
- entity_type in (`answer`, `session`, `profile`)
- status in (`queued`, `started`, `retry`, `succeeded`, `failed`, `dead`)
- unique (`idempotency_key`)
- check `attempt_no >= 0`
- check `max_attempts > 0`

### indexes
- index on (`status`, `scheduled_at`)
- index on `session_id`
- unique index on `idempotency_key`

---

## 3.12. audit_logs

Назначение: аудит критичных действий.

### columns
- `id uuid pk`
- `actor_user_id uuid null references mindtrace.users(id) on delete set null`
- `action text not null`
- `entity_type text not null`
- `entity_id uuid null`
- `session_id uuid null references mindtrace.sessions(id) on delete set null`
- `payload_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`

### indexes
- index on (`entity_type`, `entity_id`)
- index on `session_id`
- index on `created_at`

---

## 4. Правила целостности

### 4.1. Активная таксономия
В системе в MVP должна быть одна активная `taxonomy_version`.
Это лучше контролировать сервисным слоем.
При желании позже можно добавить partial unique index на `status = 'active'`.

### 4.2. Порядок вопросов
Поле `sessions.current_question_order` должно соответствовать следующему ожидаемому вопросу.
Это правило держим в backend service layer, не в SQL constraint.

### 4.3. Ревизии ответов
Новый ответ на тот же вопрос создаётся как новая строка в `answers`:
- старый current → `is_current = false`
- новый ответ → `is_current = true`
- `revision_no` увеличивается на 1

### 4.4. Final profile
На одну сессию только один final profile.
Гарантируется unique index по `session_id`.

### 4.5. Prompt traceability
Каждый AI-результат обязан ссылаться на `prompt_version_id`.

---

## 5. Обязательные SQL-объекты для первой миграции

Первая миграция должна создать:

- schema `mindtrace`
- все 12 таблиц
- все FK
- все unique constraints
- все check constraints
- все partial indexes
- все gin indexes
- расширение для генерации UUID:
  - либо `pgcrypto`
  - либо `uuid-ossp`

Решение:
используем `pgcrypto` и `gen_random_uuid()`.

---

## 6. Что должно войти в первую Alembic migration

### обязательно
- `create schema if not exists mindtrace`
- `create extension if not exists pgcrypto`
- создание всех таблиц
- создание индексов
- создание partial unique indexes вручную через SQL
- создание gin indexes вручную через SQL
- down migration на удаление в обратном порядке

---

## 7. Порядок создания объектов в migration

1. schema + extension
2. `users`
3. `taxonomy_versions`
4. `questions`
5. `sessions`
6. `answers`
7. `prompt_versions`
8. `answer_extractions`
9. `session_aggregates`
10. `final_profiles`
11. `expert_reviews`
12. `ai_jobs`
13. `audit_logs`
14. indexes
15. partial indexes
16. gin indexes

---

## 8. Что является baseline v1

DB schema v1 считается утверждённой, если в первой миграции реализованы:

- полный доменный каркас
- хранение промежуточных AI-результатов
- хранение финального профиля
- экспертная оценка
- очередь AI-job’ов
- аудит действий
- идемпотентность ответа и AI-задач
