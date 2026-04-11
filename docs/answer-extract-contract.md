# Answer Extract Contract

## 1. Назначение `answer_extract`
answer_extract возвращает нормализованный результат анализа одного ответа.

Он не строит финальный профиль.
Он делает только это:

оценивает пригодность ответа к анализу
извлекает диагностические сигналы
привязывает сигналы к evidence
отмечает противоречия и риски интерпретации
возвращает строгий JSON для сохранения в БД и дальнейшей агрегации

## 2. Root schema contract
| field name            | type                       | required | description                                                                                 |
| --------------------- | -------------------------- | -------: | ------------------------------------------------------------------------------------------- |
| `schema_version`      | `string`                   |      yes | Версия контракта. Для MVP фиксируем `answer_extraction_v1`.                                 |
| `taxonomy_version_id` | `string(uuid)`             |      yes | Версия диагностической taxonomy, по которой сделан extraction.                              |
| `question_id`         | `string(uuid)`             |      yes | ID вопроса.                                                                                 |
| `question_code`       | `string`                   |      yes | Стабильный код вопроса, например `q_001`.                                                   |
| `answer_id`           | `string(uuid)`             |      yes | ID ответа, который анализировался.                                                          |
| `analysis`            | `object`                   |      yes | Метаданные пригодности и качества ответа.                                                   |
| `signals`             | `array[SignalItem]`        |      yes | Нормализованные диагностические сигналы. Может быть пустым массивом, если ответ непригоден. |
| `contradictions`      | `array[ContradictionItem]` |      yes | Внутренние противоречия внутри одного ответа. Может быть пустым массивом.                   |
| `risk_flags`          | `array[RiskFlagItem]`      |      yes | Риски интерпретации ответа. Может быть пустым массивом.                                     |
| `summary`             | `string`                   |      yes | Короткая сводка по одному ответу для backend/expert layer.                                  |
| `overall_confidence`  | `number`                   |      yes | Общая уверенность в extraction, диапазон `0..1`.                                            |


## 3. Поле `analysis`
| field name             | type             | required | description                                                                   |
| ---------------------- | ---------------- | -------: | ----------------------------------------------------------------------------- |
| `is_usable`            | `boolean`        |      yes | Можно ли использовать ответ в диагностической агрегации.                      |
| `adequacy`             | `string`         |      yes | Общая достаточность ответа: `low`, `medium`, `high`.                          |
| `language_code`        | `string \| null` |      yes | Код языка ответа, например `ru`, `en`, `ko`. Если определить нельзя — `null`. |
| `answer_quality_flags` | `array[string]`  |      yes | Технические/аналитические флаги качества ответа. Может быть пустым массивом.  |

Допустимые значения answer_quality_flags

Минимально фиксируем:

too_short
generic
off_topic
unclear
contradictory_inside_answer
emotionally_charged
socially_desirable
template_like

## 4. Поле `signals`
| field name    | type                  | required | description                                                                          |
| ------------- | --------------------- | -------: | ------------------------------------------------------------------------------------ |
| `signal_code` | `string`              |      yes | Машинный код сигнала. Должен соответствовать taxonomy rules.                         |
| `domain`      | `string`              |      yes | Диагностический домен сигнала. Для MVP: `thinking` или `values`.                     |
| `label`       | `string`              |      yes | Нормализованная интерпретация сигнала, например `high_reflection`, `growth_leaning`. |
| `score`       | `number`              |      yes | Сила выраженности сигнала, диапазон `0..1`.                                          |
| `confidence`  | `number`              |      yes | Уверенность модели в этом сигнале, диапазон `0..1`.                                  |
| `evidence`    | `array[EvidenceItem]` |      yes | Основания сигнала. Для usable-ответа у сигнала должен быть минимум 1 evidence.       |
| `rationale`   | `string`              |      yes | Короткое объяснение, почему сигнал был извлечён.                                     |

Допустимые domain
thinking
values
Примеры signal_code для MVP

Thinking:

reflection_depth
reasoning_style
decision_style
uncertainty_handling
agency_orientation
emotional_regulation

Values:

value_priority
social_orientation
stability_vs_change
security_vs_growth
autonomy_vs_belonging

## 5. Поле `evidence`
| field name | type     | required | description                                            |
| ---------- | -------- | -------: | ------------------------------------------------------ |
| `text`     | `string` |      yes | Короткий фрагмент ответа, на который опирается сигнал. |
| `kind`     | `string` |      yes | Тип evidence. Для MVP: `quote` или `paraphrase`.       |

Допустимые kind
quote
paraphrase

## 6. Поле `contradictions`
| field name     | type            | required | description                                                         |
| -------------- | --------------- | -------: | ------------------------------------------------------------------- |
| `type`         | `string`        |      yes | Тип противоречия. Для `answer_extract` сейчас фиксируем `internal`. |
| `description`  | `string`        |      yes | Что именно противоречиво внутри одного ответа.                      |
| `severity`     | `string`        |      yes | Важность противоречия: `low`, `medium`, `high`.                     |
| `signal_codes` | `array[string]` |       no | Какие сигналы затронуты этим противоречием.                         |

Допустимые type
internal

## 7. Поле `risk_flags`
| field name    | type     | required | description                               |
| ------------- | -------- | -------: | ----------------------------------------- |
| `code`        | `string` |      yes | Машинный код риска интерпретации.         |
| `severity`    | `string` |      yes | Степень влияния: `low`, `medium`, `high`. |
| `description` | `string` |      yes | Короткое объяснение риска.                |

Допустимые code для MVP
insufficient_data
generic_response
off_topic_response
social_desirability_risk
high_emotional_distortion
internal_contradiction_risk

## 8. Обязательные правила контракта
8.1.

schema_version всегда:

"answer_extraction_v1"
8.2.

signals, contradictions, risk_flags, answer_quality_flags — всегда массивы.
Не null.

8.3.

Если analysis.is_usable = false, то:

signals может быть пустым
overall_confidence обычно низкий
должен быть хотя бы один answer_quality_flag или risk_flag
8.4.

Если analysis.is_usable = true, то:

signals должен содержать минимум 1 элемент
у каждого SignalItem должен быть минимум 1 evidence
8.5.

Все signal_code должны быть разрешены текущей taxonomy_version.

8.6.

score и confidence везде только в диапазоне:

0.0 <= value <= 1.0
8.7.

summary — короткая сводка на 1–3 предложения, без финальных диагнозов и без построения итогового профиля.

## 9. Backend mapping
| DB field            | source                                             |
| ------------------- | -------------------------------------------------- |
| `stage_code`        | `"answer_extract"`                                 |
| `normalized_output` | весь `AnswerExtractResult`                         |
| `confidence_score`  | `overall_confidence`                               |
| `prompt_version_id` | активная prompt version для stage `answer_extract` |
| `input_snapshot`    | answer text + question context + taxonomy context  |
| `status`            | `done` / `failed`                                  |
| `raw_output_text`   | сырой ответ модели до нормализации                 |

## 10. Example JSON
```json
{
  "schema_version": "answer_extraction_v1",
  "taxonomy_version_id": "738c27b6-255c-4e6a-99fa-d801a10e6fdc",
  "question_id": "ea3852a3-9a98-4773-9c1f-b146319e1164",
  "question_code": "q_001",
  "answer_id": "d2a4f6e1-9f44-4db0-a083-8126f2a37012",
  "analysis": {
    "is_usable": true,
    "adequacy": "high",
    "language_code": "ru",
    "answer_quality_flags": []
  },
  "signals": [
    {
      "signal_code": "reflection_depth",
      "domain": "thinking",
      "label": "high_reflection",
      "score": 0.82,
      "confidence": 0.86,
      "evidence": [
        {
          "text": "Мне важно понять, почему я так реагирую",
          "kind": "quote"
        }
      ],
      "rationale": "Ответ содержит самонаблюдение и причинно-следственную рефлексию."
    },
    {
      "signal_code": "security_vs_growth",
      "domain": "values",
      "label": "growth_leaning",
      "score": 0.68,
      "confidence": 0.73,
      "evidence": [
        {
          "text": "я выбираю сложный путь, если понимаю, что он меня развивает",
          "kind": "quote"
        }
      ],
      "rationale": "Ответ выражает приоритет развития над комфортом."
    }
  ],
  "contradictions": [],
  "risk_flags": [],
  "summary": "Ответ пригоден для анализа. Выражены рефлексивность и ориентация на развитие.",
  "overall_confidence": 0.81
}