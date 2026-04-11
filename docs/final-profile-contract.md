## 1. Назначение final_profile_build

final_profile_build собирает итоговый диагностический профиль по завершённой или достаточно покрытой сессии.

Он строится не из сырых ответов напрямую, а из:

latest successful session_aggregate
latest successful answer_extract при необходимости traceability
текущей taxonomy_version

Его задача:

сформировать финальный thinking profile
сформировать финальный values profile
выделить устойчивые паттерны
выделить tensions и риски
подготовить user-facing представление
подготовить expert-facing представление
вернуть структурированный JSON для сохранения в final_profiles.profile_json


## 2. Root schema contract
Корневой объект FinalProfileBuildResult

| field name            | type                       | required | description                                                                  |
| --------------------- | -------------------------- | -------: | ---------------------------------------------------------------------------- |
| `schema_version`      | `string`                   |      yes | Версия контракта. Для MVP: `final_profile_v1`.                               |
| `taxonomy_version_id` | `string(uuid)`             |      yes | Версия taxonomy, в рамках которой построен профиль.                          |
| `session_id`          | `string(uuid)`             |      yes | ID диагностической сессии.                                                   |
| `readiness`           | `ReadinessMeta`            |      yes | Готовность профиля и общая пригодность к публикации.                         |
| `thinking_profile`    | `ProfileSection`           |      yes | Итоговый профиль мышления.                                                   |
| `values_profile`      | `ProfileSection`           |      yes | Итоговый профиль ценностей.                                                  |
| `key_patterns`        | `array[PatternItem]`       |      yes | Главные устойчивые паттерны, которые можно показать пользователю и эксперту. |
| `tensions`            | `array[TensionItem]`       |      yes | Внутренние напряжения и неоднозначности профиля.                             |
| `risk_flags`          | `array[FinalRiskFlagItem]` |      yes | Риски интерпретации финального профиля.                                      |
| `evidence_basis`      | `EvidenceBasisMeta`        |      yes | На чём держится финальный профиль по данным.                                 |
| `user_view`           | `UserView`                 |      yes | То, что можно отдавать пользователю в интерфейс.                             |
| `expert_view`         | `ExpertView`               |      yes | То, что должен видеть эксперт в панели.                                      |
| `overall_confidence`  | `number`                   |      yes | Общая уверенность итогового профиля, диапазон `0..1`.                        |


## 3. Поле readiness
Объект ReadinessMeta

| field name                  | type      | required | description                                                 |
| --------------------------- | --------- | -------: | ----------------------------------------------------------- |
| `is_complete`               | `boolean` |      yes | Профиль считается завершённым и пригодным для выдачи.       |
| `coverage_ratio`            | `number`  |      yes | Насколько сессия покрывает нужный минимум, диапазон `0..1`. |
| `minimum_coverage_reached`  | `boolean` |      yes | Достигнут ли минимальный порог покрытия.                    |
| `can_be_shown_to_user`      | `boolean` |      yes | Можно ли отдавать профиль пользователю.                     |
| `can_be_reviewed_by_expert` | `boolean` |      yes | Можно ли отдавать профиль эксперту на ревью.                |


## 4. Поля thinking_profile и values_profile
Объект ProfileSection

| field name   | type                          | required | description                                                                    |
| ------------ | ----------------------------- | -------: | ------------------------------------------------------------------------------ |
| `summary`    | `string`                      |      yes | Короткая сводка по секции.                                                     |
| `dimensions` | `array[ProfileDimensionItem]` |      yes | Набор итоговых измерений внутри секции. Может быть пустым при слабом покрытии. |


## 5. Поле dimensions
Объект ProfileDimensionItem

| field name              | type            | required | description                                                 |
| ----------------------- | --------------- | -------: | ----------------------------------------------------------- |
| `dimension_code`        | `string`        |      yes | Код измерения профиля.                                      |
| `label`                 | `string`        |      yes | Итоговая интерпретация измерения.                           |
| `score`                 | `number`        |      yes | Выраженность измерения, диапазон `0..1`.                    |
| `confidence`            | `number`        |      yes | Уверенность в этом измерении, диапазон `0..1`.              |
| `support_count`         | `integer`       |      yes | Сколько агрегированных сигналов поддерживают это измерение. |
| `based_on_signal_codes` | `array[string]` |      yes | Из каких сигналов собрано это измерение.                    |

Примеры dimension_code для MVP

Thinking:

- reflection_depth
- reasoning_style
- decision_style
- uncertainty_handling
- agency_orientation
- emotional_regulation

Values:

- value_priority
- social_orientation
- stability_vs_change
- security_vs_growth
- autonomy_vs_belonging


## 6. Поле key_patterns
Объект PatternItem

| field name    | type     | required | description                             |
| ------------- | -------- | -------: | --------------------------------------- |
| `code`        | `string` |      yes | Машинный код паттерна.                  |
| `title`       | `string` |      yes | Короткое название паттерна.             |
| `description` | `string` |      yes | Объяснение паттерна простым языком.     |
| `strength`    | `string` |      yes | Сила паттерна: `low`, `medium`, `high`. |

Примеры code для MVP
- reflective_orientation
- growth_orientation
- deliberative_decision_making
- external_validation_sensitivity


## 7. Поле tensions
- Объект TensionItem

| field name        | type            | required | description                                       |
| ----------------- | --------------- | -------: | ------------------------------------------------- |
| `code`            | `string`        |      yes | Машинный код tension.                             |
| `description`     | `string`        |      yes | Что именно находится в напряжении внутри профиля. |
| `severity`        | `string`        |      yes | Значимость: `low`, `medium`, `high`.              |
| `dimension_codes` | `array[string]` |       no | Какие измерения участвуют в tension.              |

Примеры code
- autonomy_vs_approval
- growth_vs_security
- reflection_vs_overthinking


## 8. Поле risk_flags
Объект FinalRiskFlagItem

| field name    | type     | required | description                                          |
| ------------- | -------- | -------: | ---------------------------------------------------- |
| `code`        | `string` |      yes | Машинный код риска интерпретации финального профиля. |
| `severity`    | `string` |      yes | Степень влияния: `low`, `medium`, `high`.            |
| `description` | `string` |      yes | Короткое объяснение риска.                           |

Примеры code для MVP
- low_profile_confidence
- insufficient_values_coverage
- high_internal_tension
- profile_instability_risk


## 9. Поле evidence_basis
Объект EvidenceBasisMeta

| field name            | type      | required | description                                        |
| --------------------- | --------- | -------: | -------------------------------------------------- |
| `usable_answers`      | `integer` |      yes | Сколько usable answers вошло в финальный профиль.  |
| `aggregated_signals`  | `integer` |      yes | Сколько session-level signals использовано.        |
| `strong_dimensions`   | `integer` |      yes | Сколько измерений имеют достаточную уверенность.   |
| `contradiction_count` | `integer` |      yes | Сколько противоречий осталось на финальном уровне. |


## 10. Поле user_view
Объект UserView

| field name      | type            | required | description                                        |
| --------------- | --------------- | -------: | -------------------------------------------------- |
| `title`         | `string`        |      yes | Заголовок результата для пользователя.             |
| `short_summary` | `string`        |      yes | Короткая понятная сводка без технических терминов. |
| `strengths`     | `array[string]` |      yes | Основные сильные стороны.                          |
| `growth_edges`  | `array[string]` |      yes | Зоны роста в нейтральной формулировке.             |
| `disclaimers`   | `array[string]` |      yes | Ограничения интерпретации результата.              |


## 11. Поле expert_view
Объект ExpertView

| field name                | type            | required | description                                         |
| ------------------------- | --------------- | -------: | --------------------------------------------------- |
| `profile_summary`         | `string`        |      yes | Сводка для экспертной панели.                       |
| `supporting_signal_codes` | `array[string]` |      yes | Какие signal_code сильнее всего поддержали профиль. |
| `notable_contradictions`  | `array[string]` |      yes | Наиболее значимые противоречия.                     |
| `unresolved_deficits`     | `array[string]` |      yes | Какие дефициты данных ещё остаются.                 |
| `confidence_comment`      | `string`        |      yes | Комментарий к надёжности профиля.                   |


## 12. Обязательные правила контракта
12.1.

schema_version всегда:
"final_profile_v1"

12.2.

key_patterns, tensions, risk_flags, strengths, growth_edges, disclaimers, supporting_signal_codes, notable_contradictions, unresolved_deficits — всегда массивы, не null.

12.3.

score, confidence, coverage_ratio, overall_confidence только в диапазоне:
0.0 <= value <= 1.0

12.4.

Если readiness.can_be_shown_to_user = true, то:

- user_view.short_summary обязателен
- thinking_profile и values_profile не должны быть пустыми одновременно

12.5.

Если readiness.is_complete = false, то:

- если readiness.is_complete = false, должен быть минимум 1 root-level risk_flag
- если readiness.can_be_shown_to_user = true, в user_view.disclaimers должен быть минимум 1 элемент

12.6.

final_profile_build не должен заново анализировать сырые ответы как основной источник истины.
Основной источник:

- session_aggregate
- и traceability из answer_extract

12.7.

user_view не должен содержать:

- raw evidence quotes
- технические коды
- жёсткие диагнозы
- медицинские/психиатрические утверждения

12.8.

expert_view может содержать:

- signal codes
- contradictions
- deficits
- комментарий по confidence


## 13. Backend mapping

Как этот JSON маппится на final_profiles:

| DB field            | source                                                    |
| ------------------- | --------------------------------------------------------- |
| `status`            | `ready` / `failed`                                        |
| `profile_json`      | весь `FinalProfileBuildResult`                            |
| `confidence_json`   | `{ "overall_confidence": ... }` или расширенная структура |
| `prompt_version_id` | активная prompt version для stage `final_profile_build`   |
| `raw_output_text`   | сырой ответ модели до нормализации                        |

MVP-правило для summary_text

Пока можно маппить так:

- final_profiles.summary_text = user_view.short_summary

Позже это можно выделить в отдельную стадию final_profile_summary.


## 14. Example JSON
```json
{
  "schema_version": "final_profile_v1",
  "taxonomy_version_id": "738c27b6-255c-4e6a-99fa-d801a10e6fdc",
  "session_id": "2a4c0d8d-2f7d-428d-9ef9-c35ea8f7d8d1",
  "readiness": {
    "is_complete": true,
    "coverage_ratio": 0.9,
    "minimum_coverage_reached": true,
    "can_be_shown_to_user": true,
    "can_be_reviewed_by_expert": true
  },
  "thinking_profile": {
    "summary": "Профиль мышления показывает выраженную рефлексивность и склонность к осмысленному принятию решений.",
    "dimensions": [
      {
        "dimension_code": "reflection_depth",
        "label": "high",
        "score": 0.82,
        "confidence": 0.86,
        "support_count": 3,
        "based_on_signal_codes": [
          "reflection_depth",
          "reasoning_style"
        ]
      },
      {
        "dimension_code": "decision_style",
        "label": "balanced_deliberative",
        "score": 0.71,
        "confidence": 0.74,
        "support_count": 2,
        "based_on_signal_codes": [
          "decision_style",
          "uncertainty_handling"
        ]
      }
    ]
  },
  "values_profile": {
    "summary": "Ценностный профиль указывает на ориентацию на развитие при сохранении потребности в устойчивости.",
    "dimensions": [
      {
        "dimension_code": "security_vs_growth",
        "label": "growth_leaning",
        "score": 0.68,
        "confidence": 0.73,
        "support_count": 2,
        "based_on_signal_codes": [
          "security_vs_growth"
        ]
      },
      {
        "dimension_code": "autonomy_vs_belonging",
        "label": "mixed_with_autonomy_tilt",
        "score": 0.59,
        "confidence": 0.65,
        "support_count": 2,
        "based_on_signal_codes": [
          "autonomy_vs_belonging",
          "social_orientation"
        ]
      }
    ]
  },
  "key_patterns": [
    {
      "code": "reflective_orientation",
      "title": "Выраженная рефлексивность",
      "description": "Человек склонен осмыслять собственные реакции и мотивы.",
      "strength": "high"
    },
    {
      "code": "growth_orientation",
      "title": "Ориентация на развитие",
      "description": "Развитие и движение вперёд часто ставятся выше комфорта.",
      "strength": "medium"
    }
  ],
  "tensions": [
    {
      "code": "autonomy_vs_approval",
      "description": "Есть напряжение между автономностью и потребностью в подтверждении со стороны.",
      "severity": "medium",
      "dimension_codes": [
        "autonomy_vs_belonging"
      ]
    }
  ],
  "risk_flags": [],
  "evidence_basis": {
    "usable_answers": 9,
    "aggregated_signals": 8,
    "strong_dimensions": 4,
    "contradiction_count": 1
  },
  "user_view": {
    "title": "Ваш профиль MindTrace",
    "short_summary": "У вас выраженная склонность к рефлексии и осмысленному принятию решений. При этом развитие для вас важно, но иногда оно сталкивается с потребностью в подтверждении и устойчивости.",
    "strengths": [
      "Умение замечать свои внутренние реакции",
      "Склонность принимать решения не импульсивно",
      "Ориентация на развитие"
    ],
    "growth_edges": [
      "Снижать зависимость от внешнего подтверждения",
      "Не уходить в избыточное обдумывание"
    ],
    "disclaimers": [
      "Профиль основан на ответах текущей сессии",
      "Некоторые зоны пока оценены с умеренной уверенностью"
    ]
  },
  "expert_view": {
    "profile_summary": "Финальный профиль устойчив по thinking-domain, values-domain покрыт умеренно. Основной tension — autonomy vs approval.",
    "supporting_signal_codes": [
      "reflection_depth",
      "reasoning_style",
      "security_vs_growth",
      "autonomy_vs_belonging"
    ],
    "notable_contradictions": [
      "Автономность декларируется вместе с выраженной чувствительностью к внешней оценке"
    ],
    "unresolved_deficits": [
      "Нужна более плотная проверка values-profile по нескольким вопросам"
    ],
    "confidence_comment": "Профиль пригоден для выдачи пользователю и экспертного ревью."
  },
  "overall_confidence": 0.82
}
