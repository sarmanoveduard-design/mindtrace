1. Назначение session_aggregate

session_aggregate — это накопленное состояние диагностической сессии.

Он строится не из сырых ответов напрямую, а из:

- current answers
- latest successful answer_extract
- в рамках одной taxonomy_version

Его задача:

- объединить сигналы по всей сессии
- посчитать покрытие
- зафиксировать дефициты данных
- выявить межответные противоречия
- дать промежуточную confidence-оценку
- подготовить основу для final_profile_build

2. Root schema contract
## Корневой объект SessionAggregateResult

| field name            | type                                | required | description                                                                            |
| --------------------- | ----------------------------------- | -------: | -------------------------------------------------------------------------------------- |
| `schema_version`      | `string`                            |      yes | Версия контракта. Для MVP: `session_aggregate_v1`.                                     |
| `taxonomy_version_id` | `string(uuid)`                      |      yes | Версия taxonomy, в рамках которой строится агрегат.                                    |
| `session_id`          | `string(uuid)`                      |      yes | ID диагностической сессии.                                                             |
| `coverage`            | `CoverageMeta`                      |      yes | Метрики покрытия по вопросам и данным.                                                 |
| `signals`             | `array[AggregatedSignalItem]`       |      yes | Агрегированные сигналы по всей сессии. Может быть пустым массивом при слабом покрытии. |
| `deficits`            | `array[DeficitItem]`                |      yes | Какие диагностические зоны ещё недостаточно покрыты.                                   |
| `contradictions`      | `array[AggregateContradictionItem]` |      yes | Противоречия между ответами или сигналами.                                             |
| `risk_flags`          | `array[AggregateRiskFlagItem]`      |      yes | Риски интерпретации на уровне сессии.                                                  |
| `aggregate_summary`   | `string`                            |      yes | Короткая промежуточная сводка по состоянию сессии.                                     |
| `overall_confidence`  | `number`                            |      yes | Общая уверенность агрегата, диапазон `0..1`.                                           |

3. Поле coverage
## Объект CoverageMeta

| field name                    | type      | required | description                                               |
| ----------------------------- | --------- | -------: | --------------------------------------------------------- |
| `answered_questions`          | `integer` |      yes | Количество вопросов, по которым есть current answer.      |
| `required_questions`          | `integer` |      yes | Количество обязательных вопросов в taxonomy.              |
| `usable_answer_count`         | `integer` |      yes | Количество ответов, пригодных для агрегации.              |
| `coverage_ratio`              | `number`  |      yes | Отношение usable / required, диапазон `0..1`.             |
| `is_minimum_coverage_reached` | `boolean` |      yes | Достигнут ли минимальный порог для осмысленного агрегата. |

4. Поле signals
## Объект AggregatedSignalItem

| field name          | type                  | required | description                                                      |
| ------------------- | --------------------- | -------: | ---------------------------------------------------------------- |
| `signal_code`       | `string`              |      yes | Код агрегируемого сигнала.                                       |
| `domain`            | `string`              |      yes | Диагностический домен: `thinking` или `values`.                  |
| `label`             | `string`              |      yes | Нормализованная итоговая интерпретация сигнала на уровне сессии. |
| `score`             | `number`              |      yes | Агрегированная сила сигнала, диапазон `0..1`.                    |
| `confidence`        | `number`              |      yes | Уверенность в агрегированном сигнале, диапазон `0..1`.           |
| `support_count`     | `integer`             |      yes | Сколько answer_extract поддерживают этот сигнал.                 |
| `question_codes`    | `array[string]`       |      yes | Из каких вопросов пришла поддержка сигнала.                      |
| `evidence_summary`  | `array[string]`       |      yes | Краткие основания без полного raw-цитирования.                   |
| `source_answer_ids` | `array[string(uuid)]` |      yes | Какие answer_id легли в этот сигнал.                             |

Допустимые domain
- thinking
- values

5. Поле deficits
## Объект DeficitItem

| field name                   | type            | required | description                                                            |
| ---------------------------- | --------------- | -------: | ---------------------------------------------------------------------- |
| `code`                       | `string`        |      yes | Машинный код дефицита покрытия.                                        |
| `domain`                     | `string`        |      yes | Где именно не хватает данных: `thinking`, `values` или `general`.      |
| `description`                | `string`        |      yes | Что именно пока нельзя уверенно определить.                            |
| `severity`                   | `string`        |      yes | Насколько дефицит влияет на итоговый профиль: `low`, `medium`, `high`. |
| `recommended_question_codes` | `array[string]` |       no | Какие вопросы потенциально закрывают дефицит.                          |

Примеры code для MVP
- low_reflection_coverage
- low_values_coverage
- insufficient_decision_signals
- insufficient_confidence
- too_many_unusable_answers

6. Поле contradictions
## Объект AggregateContradictionItem

| field name       | type            | required | description                                                |
| ---------------- | --------------- | -------: | ---------------------------------------------------------- |
| `type`           | `string`        |      yes | Тип противоречия. Для MVP: `cross_answer`, `cross_signal`. |
| `description`    | `string`        |      yes | Что именно противоречит между ответами или сигналами.      |
| `severity`       | `string`        |      yes | Важность: `low`, `medium`, `high`.                         |
| `signal_codes`   | `array[string]` |       no | Какие сигналы участвуют в противоречии.                    |
| `question_codes` | `array[string]` |       no | В каких вопросах это проявилось.                           |

Допустимые type
- cross_answer
- cross_signal

7. Поле risk_flags
## Объект AggregateRiskFlagItem

| field name    | type     | required | description                               |
| ------------- | -------- | -------: | ----------------------------------------- |
| `code`        | `string` |      yes | Машинный код риска на уровне сессии.      |
| `severity`    | `string` |      yes | Степень влияния: `low`, `medium`, `high`. |
| `description` | `string` |      yes | Короткое объяснение риска.                |

Примеры code для MVP
- low_session_coverage
- high_answer_noise
- cross_answer_inconsistency
- low_aggregate_confidence
- values_profile_unstable

8. Обязательные правила контракта
8.1.

schema_version всегда:
"session_aggregate_v1"

8.2.

signals, deficits, contradictions, risk_flags — всегда массивы.
Не null.

8.3.

coverage.coverage_ratio, score, confidence, overall_confidence:

только 0.0 <= value <= 1.0

8.4.

Если coverage.is_minimum_coverage_reached = false, то:

signals может быть частично заполнен
deficits должен содержать минимум 1 элемент
overall_confidence не должен быть высоким

8.5.

Каждый AggregatedSignalItem.support_count >= 1

8.6.

Каждый агрегированный сигнал должен быть получен только из:

latest successful answer_extract
current answer revisions
той же taxonomy_version

8.7.

aggregate_summary — это промежуточная аналитическая сводка, а не финальный профиль пользователя.

9. Backend mapping

## Как этот JSON маппится на session_aggregates:

| DB field            | source                                                               |
| ------------------- | -------------------------------------------------------------------- |
| `stage_code`        | `"session_aggregate"`                                                |
| `aggregate_json`    | весь `SessionAggregateResult`                                        |
| `coverage_json`     | поле `coverage`                                                      |
| `confidence_json`   | `{ "overall_confidence": ... }` или расширенная confidence-структура |
| `prompt_version_id` | активная prompt version для stage `session_aggregate`                |
| `status`            | `done` / `failed`                                                    |
| `raw_output_text`   | сырой ответ модели до нормализации                                   |

10. Example JSON

## 10. Example JSON

```json
{
  "schema_version": "session_aggregate_v1",
  "taxonomy_version_id": "738c27b6-255c-4e6a-99fa-d801a10e6fdc",
  "session_id": "2a4c0d8d-2f7d-428d-9ef9-c35ea8f7d8d1",
  "coverage": {
    "answered_questions": 3,
    "required_questions": 10,
    "usable_answer_count": 3,
    "coverage_ratio": 0.3,
    "is_minimum_coverage_reached": true
  },
  "signals": [
    {
      "signal_code": "reflection_depth",
      "domain": "thinking",
      "label": "high_reflection",
      "score": 0.79,
      "confidence": 0.84,
      "support_count": 2,
      "question_codes": ["q_001", "q_002"],
      "evidence_summary": [
        "Причинно-следственная рефлексия",
        "Самонаблюдение"
      ],
      "source_answer_ids": [
        "d2a4f6e1-9f44-4db0-a083-8126f2a37012",
        "0cfcf1b8-a7d6-4f20-8536-e4a4db6dce6a"
      ]
    },
    {
      "signal_code": "security_vs_growth",
      "domain": "values",
      "label": "growth_leaning",
      "score": 0.68,
      "confidence": 0.73,
      "support_count": 1,
      "question_codes": ["q_001"],
      "evidence_summary": [
        "Приоритет развития над комфортом"
      ],
      "source_answer_ids": [
        "d2a4f6e1-9f44-4db0-a083-8126f2a37012"
      ]
    }
  ],
  "deficits": [
    {
      "code": "low_values_coverage",
      "domain": "values",
      "description": "Пока недостаточно ответов для устойчивой оценки ценностного профиля.",
      "severity": "medium",
      "recommended_question_codes": ["q_004", "q_005"]
    }
  ],
  "contradictions": [],
  "risk_flags": [],
  "aggregate_summary": "Есть ранние устойчивые признаки рефлексивности и ориентации на развитие, но ценностный профиль ещё покрыт недостаточно.",
  "overall_confidence": 0.76
}
